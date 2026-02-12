import pandas as pd
def predict_nutrition(age, weight, height):
    weight = float(weight)
    height = float(height)

    bmi = weight / ((height / 100) ** 2)

    if bmi < 14:
        return {
            "status": "Underweight",
            "advice": "Increase protein intake. Include milk, eggs, fruits, and vegetables."
        }
    elif bmi < 18:
        return {
            "status": "Normal",
            "advice": "Maintain balanced diet and regular activity."
        }
    else:
        return {
            "status": "Overweight",
            "advice": "Reduce junk food and increase physical activity."
        }
