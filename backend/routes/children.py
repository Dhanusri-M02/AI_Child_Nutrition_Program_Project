from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from utils import send_alert_email

children_bp = Blueprint('children', __name__)

@children_bp.route('/children', methods=['POST'])
@jwt_required()
def add_child():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert child
        cursor.execute("""
            INSERT INTO children (parent_id, name, sex, age, weight, height, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['parent_id'], data['name'], data['sex'], data['age'], 
              data['weight'], data['height'], current_user['user_id']))
        
        child_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        # Send malnutrition alert if needed
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM children WHERE id = %s", (child_id,))
        child = cursor.fetchone()
        
        return jsonify(child), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@children_bp.route('/children', methods=['GET'])
@jwt_required()
def get_children():
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if current_user['role'] == 'parent':
        cursor.execute("""
            SELECT c.*, u.name as parent_name 
            FROM children c 
            JOIN users u ON c.parent_id = u.id 
            WHERE c.parent_id = %s
        """, (current_user['user_id'],))
    else:
        cursor.execute("""
            SELECT c.*, u.name as parent_name 
            FROM children c 
            JOIN users u ON c.parent_id = u.id
        """)
    
    children = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(children)

@children_bp.route('/children/<child_id>', methods=['DELETE'])
@jwt_required()
def delete_child(child_id):
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM children WHERE id = %s", (child_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Child deleted'})

@children_bp.route('/health-records', methods=['POST'])
@jwt_required()
def add_health_record():
    data = request.get_json()
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO health_records (child_id, recorded_by, sex, age, weight, height, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (data['child_id'], current_user['user_id'], data['sex'], data['age'], 
          data['weight'], data['height'], data['status']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Update case count
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO case_counts (worker_id, status, count, date)
        VALUES (%s, %s, 1, CURDATE())
        ON DUPLICATE KEY UPDATE count = count + 1
    """, (current_user['user_id'], data['status']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Record saved'})

@children_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM health_records 
        WHERE recorded_by = %s 
        GROUP BY status
    """, (current_user['user_id'],))
    
    stats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({'health_stats': stats})

if __name__ == '__main__':
    print("Children routes loaded")

