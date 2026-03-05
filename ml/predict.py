import joblib
import os
import numpy as np

model_path = os.path.join(os.path.dirname(__file__), "nutrition_model.pkl")
model = joblib.load(model_path)


def predict_nutrition(sex, age, weight, height):

    if height <= 0 or weight <= 0:
        return {
            "status": "Invalid Input",
            "advice": "Please enter valid values."
        }

    data = np.array([[sex, age, weight, height]])
    prediction = model.predict(data)[0]

    if prediction == 0:
        return {
            "status": "Underweight",
            "advice": "Increase protein-rich foods."
        }
    elif prediction == 1:
        return {
            "status": "Normal",
            "advice": "Maintain balanced diet."
        }
    else:
        return {
            "status": "Overweight",
            "advice": "Reduce junk food intake."
        }