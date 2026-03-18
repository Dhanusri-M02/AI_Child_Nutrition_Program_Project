from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import bcrypt
from db import get_db_connection
from datetime import datetime, timedelta
from utils import send_otp_email, generate_otp, require_admin

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Register (same)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']
    role = data['role']

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, hashed, role)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User registered successfully"})

# Login - For admin, send OTP
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # Non-admin (parent, nutrition_worker): JWT immediately
        if user['role'] != 'admin':
            token = create_access_token(identity={'user_id': user['id'], 'role': user['role'], 'name': user['name']}, fresh=True)
            conn.close()
            return jsonify({
                "message": "Login successful",
                "token": token,
                "role": user['role'],
                "user_id": user['id']
            }), 200
        
        # Admin: OTP flow
        otp = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=5)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admin_otps (user_id, otp, expires_at, ip_address) VALUES (%s, %s, %s, %s)",
            (user['id'], otp, expires_at, request.remote_addr)
        )
        otp_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        if send_otp_email(email, otp):
            return jsonify({"message": "OTP sent to email (check console)", "otp_id": otp_id})
        else:
            return jsonify({"message": "Email send failed"}), 500
    else:
        conn.close()
        return jsonify({"message": "Invalid credentials"}), 401

# Admin OTP Verify
@auth_bp.route('/admin/verify-otp', methods=['POST'])
def verify_admin_otp():
    data = request.json
    otp_id = data['otp_id']
    otp = data['otp']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM admin_otps ao JOIN users u ON ao.user_id = u.id WHERE ao.id = %s AND ao.expires_at > NOW() AND ao.attempts < 3",
        (otp_id,)
    )
    otp_record = cursor.fetchone()

    if otp_record and otp_record['otp'] == otp:
        # Success - delete OTP, issue JWT
        cursor.execute("DELETE FROM admin_otps WHERE id = %s", (otp_id,))
        cursor.execute("UPDATE admin_otps SET attempts = attempts + 1 WHERE id = %s", (otp_id,))
        conn.commit()
        
        token = create_access_token(
            identity={'user_id': otp_record['id'], 'role': otp_record['role'], 'name': otp_record['name']}, 
            fresh=True
        )
        cursor.close()
        conn.close()
        return jsonify({
            "message": "Login successful",
            "token": token,
            "role": otp_record['role'],
            "user_id": otp_record['id']
        }), 200
    else:
        # Increment attempts
        cursor.execute("UPDATE admin_otps SET attempts = attempts + 1 WHERE id = %s", (otp_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Invalid or expired OTP"}), 401

auth_bp.require_admin = require_admin  # Attach decorator

