import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import numpy as np

# Load the balanced dataset
df = pd.read_csv("data/child_nutrition_balanced_dataset_1000.csv")

print("Original dataset shape:", df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Check class distribution
print("\nNutrition Status distribution:")
print(df['Nutrition_Status'].value_counts())

# Encode Gender: Male=1, Female=0
df['Sex'] = df['Gender'].map({'Male': 1, 'Female': 0})

# Encode Nutrition_Status: Underweight=0, Normal=1, Overweight=2
status_mapping = {'Underweight': 0, 'Normal': 1, 'Overweight': 2}
df['status'] = df['Nutrition_Status'].map(status_mapping)

print("\nStatus mapping:", status_mapping)
print("\nStatus distribution:")
print(df['status'].value_counts())

# Prepare features - using Age, Sex, Weight, Height
X = df[['Sex', 'Age', 'Weight_kg', 'Height_cm']].values
y = df['status'].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

print("\nTraining class distribution:")
unique, counts = np.unique(y_train, return_counts=True)
for u, c in zip(unique, counts):
    status_name = ["Underweight", "Normal", "Overweight"][u]
    print(f"  {status_name}: {c}")

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print("\nModel Accuracy:", accuracy)

# Check predictions
y_pred = model.predict(X_test)
print("\nPrediction distribution on test set:")
unique, counts = np.unique(y_pred, return_counts=True)
for u, c in zip(unique, counts):
    status_name = ["Underweight", "Normal", "Overweight"][u]
    print(f"  {status_name}: {c}")

print("\nActual test set distribution:")
unique, counts = np.unique(y_test, return_counts=True)
for u, c in zip(unique, counts):
    status_name = ["Underweight", "Normal", "Overweight"][u]
    print(f"  {status_name}: {c}")

# Feature importance
print("\nFeature Importance:")
feature_names = ['Sex', 'Age', 'Weight_kg', 'Height_cm']
for name, imp in zip(feature_names, model.feature_importances_):
    print(f"  {name}: {imp:.4f}")

# Save model
os.makedirs("ml", exist_ok=True)
model_path = os.path.join("ml", "nutrition_model.pkl")
joblib.dump(model, model_path)

print("\nModel saved successfully to:", model_path)
print("Done!")
