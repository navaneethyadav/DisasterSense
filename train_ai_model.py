import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# File paths
DATA_FILE = "data/sensor_data.csv"
MODEL_FILE = "ai_disaster_model.pkl"

# Load sensor data
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"{DATA_FILE} not found. Please generate sensor_data.csv first.")

data = pd.read_csv(DATA_FILE)

# Fill missing columns if any
for col in ['temperature', 'humidity', 'pressure', 'disaster_type']:
    if col not in data.columns:
        data[col] = 0

# Create severity label (example logic)
# You can adjust thresholds based on real use-case
def severity_label(row):
    score = row['temperature'] + (100 - row['humidity'])/2 + (1020 - row['pressure'])
    if score < 50:
        return "Safe"
    elif score < 120:
        return "Warning"
    else:
        return "Critical"

data['severity'] = data.apply(severity_label, axis=1)

# Encode target labels
le = LabelEncoder()
data['severity_encoded'] = le.fit_transform(data['severity'])

# Features and target
X = data[['temperature', 'humidity', 'pressure']]
y = data['severity_encoded']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and label encoder
joblib.dump(model, MODEL_FILE)
joblib.dump(le, "label_encoder.pkl")

print(f"✅ AI model trained and saved as {MODEL_FILE}")
