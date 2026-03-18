import os
from dotenv import load_dotenv
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from db import get_db_connection
from datetime import datetime, timedelta
import random
import string
import smtplib
from email.mime.text import MIMEText

load_dotenv()

def require_admin(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt()
        if current_user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def send_otp_email(email, otp):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not all([smtp_server, smtp_user, smtp_password]):
        print("❌ SMTP config missing - check backend/.env")
        return False
    
    msg = MIMEText(f"Your Admin Login OTP is: {otp}\n\nValid for 5 minutes only.\n\nChild Nutrition System")
    msg['Subject'] = 'Admin Login OTP - Child Nutrition System'
    msg['From'] = smtp_user
    msg['To'] = email
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        print(f"✅ OTP ({otp}) SENT to {email}")
        return True
    except Exception as e:
        print(f"❌ Email FAILED: {e}")
        return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

