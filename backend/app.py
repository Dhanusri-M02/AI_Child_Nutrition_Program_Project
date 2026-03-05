
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db_connection
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.predict import predict_nutrition

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Backend running successfully"


# ============================================
# AUTH ROUTES
# ============================================

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        # Hash password with bcrypt
        hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (data["name"], data["email"], hashed_password, data["role"])
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Signup successful"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (data["email"],)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(data["password"].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({
            "message": "Login successful",
            "role": user['role'],
            "user_id": user['id'],
            "name": user['name']
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# ============================================
# NUTRITION PREDICTION ROUTE
# ============================================

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        result = predict_nutrition(
            int(data["sex"]),
            float(data["age"]),
            float(data["weight"]),
            float(data["height"])
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "status": "Error",
            "advice": str(e)
        }), 500


# ============================================
# CHILDREN ROUTES
# ============================================

@app.route("/children", methods=["GET"])
def get_children():
    try:
        parent_id = request.args.get('parent_id')
        
        if not parent_id:
            return jsonify({"error": "parent_id required"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM children WHERE parent_id = %s ORDER BY created_at DESC",
            (parent_id,)
        )
        children = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(children), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/children", methods=["POST"])
def add_child():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO children (parent_id, name, sex, age, weight, height) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (data["parent_id"], data["name"], data["sex"], 
             data["age"], data["weight"], data["height"])
        )
        
        child_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Child added successfully", "child_id": child_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Worker adds child for a parent by email
@app.route("/children/worker-add", methods=["POST"])
def worker_add_child():
    try:
        data = request.get_json()
        
        # Find parent by email
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id FROM users WHERE email = %s AND role = 'parent'", (data["parent_email"],))
        parent = cursor.fetchone()
        
        if not parent:
            cursor.close()
            conn.close()
            return jsonify({"error": "Parent email not found"}), 404
        
        # Insert child
        cursor.execute(
            """INSERT INTO children (parent_id, name, sex, age, weight, height) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (parent["id"], data["name"], data["sex"], 
             data["age"], data["weight"], data["height"])
        )
        
        child_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Child added successfully for parent", 
            "child_id": child_id,
            "parent_id": parent["id"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/children/<int:child_id>", methods=["PUT"])
def update_child(child_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE children SET name=%s, sex=%s, age=%s, weight=%s, height=%s 
               WHERE id=%s""",
            (data["name"], data["sex"], data["age"], 
             data["weight"], data["height"], child_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Child updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/children/<int:child_id>", methods=["DELETE"])
def delete_child(child_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM children WHERE id = %s", (child_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Child deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# HEALTH RECORDS ROUTES
# ============================================

@app.route("/health-records", methods=["GET"])
def get_health_records():
    try:
        child_id = request.args.get('child_id')
        
        if not child_id:
            return jsonify({"error": "child_id required"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT hr.*, u.name as recorded_by_name 
               FROM health_records hr
               JOIN users u ON hr.recorded_by = u.id
               WHERE hr.child_id = %s 
               ORDER BY hr.recorded_at DESC""",
            (child_id,)
        )
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(records), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health-records", methods=["POST"])
def add_health_record():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get prediction result
        result = predict_nutrition(
            int(data["sex"]),
            float(data["age"]),
            float(data["weight"]),
            float(data["height"])
        )
        
        cursor.execute(
            """INSERT INTO health_records 
               (child_id, recorded_by, sex, age, weight, height, status, advice) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (data["child_id"], data["recorded_by"], data["sex"],
             data["age"], data["weight"], data["height"], 
             result.get("status", "Unknown"), result.get("advice", ""))
        )
        
        record_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Health record added successfully", 
            "record_id": record_id,
            "result": result
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# MALNUTRITION CASES ROUTES
# ============================================

@app.route("/malnutrition-cases", methods=["GET"])
def get_malnutrition_cases():
    try:
        child_id = request.args.get('child_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if child_id:
            cursor.execute(
                "SELECT * FROM malnutrition_cases WHERE child_id = %s ORDER BY detected_at DESC",
                (child_id,)
            )
        else:
            cursor.execute(
                """SELECT mc.*, c.name as child_name 
                   FROM malnutrition_cases mc
                   JOIN children c ON mc.child_id = c.id
                   ORDER BY mc.detected_at DESC"""
            )
        
        cases = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(cases), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/malnutrition-cases", methods=["POST"])
def add_malnutrition_case():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO malnutrition_cases 
               (child_id, record_id, malnutrition_type, severity, bmi, status) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (data["child_id"], data["record_id"], data["malnutrition_type"],
             data.get("severity", "none"), data.get("bmi"), data.get("status", "active"))
        )
        
        case_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Malnutrition case added", "case_id": case_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# ALERTS ROUTES
# ============================================

@app.route("/alerts", methods=["GET"])
def get_alerts():
    try:
        child_id = request.args.get('child_id')
        user_id = request.args.get('user_id')
        unread_only = request.args.get('unread_only')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT a.*, c.name as child_name FROM alerts a JOIN children c ON a.child_id = c.id WHERE 1=1"
        params = []
        
        if child_id:
            query += " AND a.child_id = %s"
            params.append(child_id)
        
        if user_id:
            query += " AND (a.assigned_to = %s OR a.assigned_to IS NULL)"
            params.append(user_id)
        
        if unread_only == 'true':
            query += " AND a.is_read = FALSE"
        
        query += " ORDER BY a.created_at DESC"
        
        cursor.execute(query, params)
        alerts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(alerts), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/alerts", methods=["POST"])
def create_alert():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO alerts 
               (child_id, alert_type, title, description, priority, assigned_to) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (data["child_id"], data["alert_type"], data["title"],
             data.get("description"), data.get("priority", "medium"), data.get("assigned_to"))
        )
        
        alert_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Alert created", "alert_id": alert_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/alerts/<int:alert_id>/read", methods=["PUT"])
def mark_alert_read(alert_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE alerts SET is_read = TRUE WHERE id = %s", (alert_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Alert marked as read"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# MONITORING PLANS ROUTES
# ============================================

@app.route("/monitoring-plans", methods=["GET"])
def get_monitoring_plans():
    try:
        child_id = request.args.get('child_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if child_id:
            cursor.execute(
                """SELECT mp.*, u.name as created_by_name 
                   FROM monitoring_plans mp
                   JOIN users u ON mp.created_by = u.id
                   WHERE mp.child_id = %s 
                   ORDER BY mp.created_at DESC""",
                (child_id,)
            )
        else:
            cursor.execute(
                """SELECT mp.*, c.name as child_name, u.name as created_by_name 
                   FROM monitoring_plans mp
                   JOIN children c ON mp.child_id = c.id
                   JOIN users u ON mp.created_by = u.id
                   ORDER BY mp.created_at DESC"""
            )
        
        plans = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(plans), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/monitoring-plans", methods=["POST"])
def create_monitoring_plan():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO monitoring_plans 
               (child_id, created_by, plan_name, goal, target_weight, target_date, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data["child_id"], data["created_by"], data.get("plan_name"),
             data.get("goal"), data.get("target_weight"), data.get("target_date"), "active")
        )
        
        plan_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Monitoring plan created", "plan_id": plan_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# FOLLOW UPS ROUTES
# ============================================

@app.route("/follow-ups", methods=["GET"])
def get_follow_ups():
    try:
        plan_id = request.args.get('monitoring_plan_id')
        child_id = request.args.get('child_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """SELECT f.*, u.name as conducted_by_name 
                   FROM follow_ups f
                   LEFT JOIN users u ON f.conducted_by = u.id
                   WHERE 1=1"""
        params = []
        
        if plan_id:
            query += " AND f.monitoring_plan_id = %s"
            params.append(plan_id)
        
        if child_id:
            query += " AND f.child_id = %s"
            params.append(child_id)
        
        query += " ORDER BY f.scheduled_date DESC"
        
        cursor.execute(query, params)
        follow_ups = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(follow_ups), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/follow-ups", methods=["POST"])
def create_follow_up():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO follow_ups 
               (monitoring_plan_id, child_id, scheduled_date, weight, height, notes, conducted_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data.get("monitoring_plan_id"), data["child_id"], data["scheduled_date"],
             data.get("weight"), data.get("height"), data.get("notes"), data.get("conducted_by"))
        )
        
        follow_up_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Follow-up scheduled", "follow_up_id": follow_up_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# INTERVENTIONS ROUTES
# ============================================

@app.route("/interventions", methods=["GET"])
def get_interventions():
    try:
        child_id = request.args.get('child_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if child_id:
            cursor.execute(
                """SELECT i.*, u.name as prescribed_by_name 
                   FROM interventions i
                   JOIN users u ON i.prescribed_by = u.id
                   WHERE i.child_id = %s
                   ORDER BY i.start_date DESC""",
                (child_id,)
            )
        else:
            cursor.execute(
                """SELECT i.*, c.name as child_name, u.name as prescribed_by_name 
                   FROM interventions i
                   JOIN children c ON i.child_id = c.id
                   JOIN users u ON i.prescribed_by = u.id
                   ORDER BY i.start_date DESC"""
            )
        
        interventions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(interventions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/interventions", methods=["POST"])
def create_intervention():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO interventions 
               (child_id, intervention_type, description, status, start_date, end_date, prescribed_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data["child_id"], data["intervention_type"], data.get("description"),
             "prescribed", data["start_date"], data.get("end_date"), data["prescribed_by"])
        )
        
        intervention_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Intervention created", "intervention_id": intervention_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# APPOINTMENTS ROUTES
# ============================================

@app.route("/appointments", methods=["GET"])
def get_appointments():
    try:
        child_id = request.args.get('child_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if child_id:
            cursor.execute(
                """SELECT a.*, u.name as created_by_name 
                   FROM appointments a
                   JOIN users u ON a.created_by = u.id
                   WHERE a.child_id = %s
                   ORDER BY a.appointment_date DESC""",
                (child_id,)
            )
        else:
            cursor.execute(
                """SELECT a.*, c.name as child_name, u.name as created_by_name 
                   FROM appointments a
                   JOIN children c ON a.child_id = c.id
                   JOIN users u ON a.created_by = u.id
                   ORDER BY a.appointment_date DESC"""
            )
        
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(appointments), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/appointments", methods=["POST"])
def create_appointment():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO appointments 
               (child_id, appointment_date, appointment_type, location, notes, status, created_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data["child_id"], data["appointment_date"], data["appointment_type"],
             data.get("location"), data.get("notes"), "scheduled", data["created_by"])
        )
        
        appointment_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Appointment scheduled", "appointment_id": appointment_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# WORKER ASSIGNMENTS ROUTES
# ============================================

@app.route("/worker-assignments", methods=["GET"])
def get_worker_assignments():
    try:
        worker_id = request.args.get('worker_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if worker_id:
            cursor.execute(
                """SELECT wa.*, c.name as child_name, c.age, u.name as assigned_by_name 
                   FROM worker_assignments wa
                   JOIN children c ON wa.child_id = c.id
                   JOIN users u ON wa.assigned_by = u.id
                   WHERE wa.nutrition_worker_id = %s AND wa.is_active = TRUE""",
                (worker_id,)
            )
        else:
            cursor.execute(
                """SELECT wa.*, c.name as child_name, u.name as worker_name, 
                          u2.name as assigned_by_name 
                   FROM worker_assignments wa
                   JOIN children c ON wa.child_id = c.id
                   JOIN users u ON wa.nutrition_worker_id = u.id
                   JOIN users u2 ON wa.assigned_by = u2.id"""
            )
        
        assignments = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(assignments), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/worker-assignments", methods=["POST"])
def create_worker_assignment():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO worker_assignments 
               (nutrition_worker_id, child_id, assigned_by) 
               VALUES (%s, %s, %s)""",
            (data["nutrition_worker_id"], data["child_id"], data["assigned_by"])
        )
        
        assignment_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Worker assigned", "assignment_id": assignment_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# SYSTEM LOGS ROUTES (Admin)
# ============================================

@app.route("/admin/logs", methods=["GET"])
def get_system_logs():
    try:
        limit = request.args.get('limit', 100)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT sl.*, u.name as user_name 
               FROM system_logs sl
               LEFT JOIN users u ON sl.user_id = u.id
               ORDER BY sl.created_at DESC
               LIMIT %s""",
            (limit,)
        )
        
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(logs), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# ADMIN ROUTES
# ============================================

@app.route("/admin/users", methods=["GET"])
def get_all_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
        )
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(users), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all parents for worker to add child
@app.route("/parents", methods=["GET"])
def get_all_parents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, name, email FROM users WHERE role = 'parent' ORDER BY name"
        )
        parents = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(parents), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/children", methods=["GET"])
def get_all_children_admin():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT c.*, u.name as parent_name, u.email as parent_email 
               FROM children c
               JOIN users u ON c.parent_id = u.id
               ORDER BY c.created_at DESC"""
        )
        children = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(children), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/health-records", methods=["GET"])
def get_all_health_records_admin():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT hr.*, c.name as child_name, u.name as recorded_by_name,
                      u.role as recorded_by_role
               FROM health_records hr
               JOIN children c ON hr.child_id = c.id
               JOIN users u ON hr.recorded_by = u.id
               ORDER BY hr.recorded_at DESC"""
        )
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(records), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/stats", methods=["GET"])
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # User stats
        cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
        user_stats = cursor.fetchall()
        
        # Children stats
        cursor.execute("SELECT COUNT(*) as total FROM children")
        total_children = cursor.fetchone()
        
        # Health records stats
        cursor.execute("SELECT status, COUNT(*) as count FROM health_records GROUP BY status")
        health_stats = cursor.fetchall()
        
        # Alerts stats
        cursor.execute("SELECT COUNT(*) as total FROM alerts WHERE is_read = FALSE")
        unread_alerts = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "user_stats": user_stats,
            "total_children": total_children,
            "health_stats": health_stats,
            "unread_alerts": unread_alerts
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

