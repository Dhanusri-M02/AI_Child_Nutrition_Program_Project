from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.auth import auth_bp
import sys
import os

from db import get_db_connection

# Add ml folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.predict import predict_nutrition

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route('/')
def home():
    return "Child Nutrition AI Backend Running"


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        sex = int(data.get("sex"))
        age = float(data.get("age"))
        weight = float(data.get("weight"))
        height = float(data.get("height"))

        # AI prediction
        result = predict_nutrition(sex, age, weight, height)

        # Calculate BMI for storage
        bmi = weight / ((height / 100) ** 2)

        # Save to MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert child
        cursor.execute(
            "INSERT INTO children (sex, age, weight, height) VALUES (%s, %s, %s, %s)",
            (sex, age, weight, height)
        )
        child_id = cursor.lastrowid

        # Insert health record
        cursor.execute(
            """
            INSERT INTO health_records (child_id, bmi, status, advice)
            VALUES (%s, %s, %s, %s)
            """,
            (child_id, bmi, result["status"], result["advice"])
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
