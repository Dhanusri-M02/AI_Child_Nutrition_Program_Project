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


@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (data["name"], data["email"], data["password"], data["role"])
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
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (data["email"], data["password"])
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


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


if __name__ == "__main__":
    app.run(debug=True)