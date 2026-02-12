import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "age": 4,
    "weight": 10,
    "height": 85
}

response = requests.post(url, json=data)

print("Response from API:")
print(response.json())
