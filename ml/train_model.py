import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import resample
import joblib
import os

# Load dataset
df = pd.read_csv("data/child_nutrition.csv")

# Keep only required columns
df = df[["Sex", "Age", "Weight", "Height", "Wasting", "Overweight", "Stunting"]]

# Create target label
def get_status(row):
    if row["Wasting"] == 1:
        return 0  # Underweight
    elif row["Overweight"] == 1:
        return 2  # Overweight
    else:
        return 1  # Normal

df["status"] = df.apply(get_status, axis=1)

print("Original class distribution:")
print(df["status"].value_counts())

# -----------------------------
# Balance dataset
# -----------------------------
df_under = df[df.status == 0]
df_normal = df[df.status == 1]
df_over = df[df.status == 2]

# Choose equal sample size
target_size = 50

df_normal_down = resample(
    df_normal,
    replace=False,
    n_samples=target_size,
    random_state=42
)

df_under_up = resample(
    df_under,
    replace=True,
    n_samples=target_size,
    random_state=42
)

df_over_up = resample(
    df_over,
    replace=True,
    n_samples=target_size,
    random_state=42
)

# Combine
df_balanced = pd.concat([df_normal_down, df_under_up, df_over_up])

print("\nBalanced class distribution:")
print(df_balanced["status"].value_counts())

# -----------------------------
# Prepare features
# -----------------------------
X = df_balanced[["Sex", "Age", "Weight", "Height"]]
y = df_balanced["status"]

# Split after balancing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# Train model
# -----------------------------
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# -----------------------------
# Evaluate model
# -----------------------------
accuracy = model.score(X_test, y_test)
print("\nModel Accuracy:", accuracy)

# -----------------------------
# Save model
# -----------------------------
os.makedirs("ml", exist_ok=True)
model_path = os.path.join("ml", "nutrition_model.pkl")
joblib.dump(model, model_path)

print("Model saved successfully")
