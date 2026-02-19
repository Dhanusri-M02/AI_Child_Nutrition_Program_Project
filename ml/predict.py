import joblib
import os
import numpy as np

# Load model
model_path = os.path.join(os.path.dirname(__file__), "nutrition_model.pkl")
model = joblib.load(model_path)

def predict_nutrition(sex, age, weight, height):
    # Prevent division or invalid inputs
    if height <= 0 or weight <= 0:
        return {
            "status": "Invalid Input",
            "advice": "Please enter valid height and weight."
        }

    data = np.array([[sex, age, weight, height]])
    prediction = model.predict(data)[0]

    if prediction == 0:
        return {
            "status": "Underweight",
            "advice": "Increase protein-rich foods like milk, eggs, and pulses."
        }
    elif prediction == 1:
        return {
            "status": "Normal",
            "advice": "Maintain balanced diet and regular activity."
        }
    else:
        return {
            "status": "Overweight",
            "advice": "Reduce junk food and increase physical activity."
        }
