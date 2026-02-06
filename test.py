from ml.predict import predict_nutrition

# Sample child data
age = 4
weight = 10   # in kg
height = 85   # in cm

result = predict_nutrition(age, weight, height)

print("Prediction:", result)
