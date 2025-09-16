import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load sensor data
data = pd.read_csv("data/sensor_data.csv")
print("Data Loaded Successfully!")
print(data.head())

# Preprocess data
X = data.drop("disaster", axis=1)  # Features
y = data["disaster"]               # Target

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
print("Data Split into Training and Testing Sets!")

# Train model
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)
print("Model Trained Successfully!")

# Test model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy*100:.2f}%")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "models/disaster_model.pkl")
print("Model Saved to 'models/disaster_model.pkl'")
