import pandas as pd

def predict_nutrition(age, weight, height):
    # Simple BMI-based logic
    bmi = weight / ((height/100) ** 2)

    if bmi < 14:
        return "Severely Malnourished"
    elif bmi < 18:
        return "Moderately Malnourished"
    else:
        return "Normal"
