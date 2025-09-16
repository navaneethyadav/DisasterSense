# create_ai_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load sensor data
try:
    data = pd.read_csv("data/sensor_data.csv")
except FileNotFoundError:
    print("sensor_data.csv not found. Make sure it's in the data/ folder.")
    exit()

# Check for required columns
required_cols = ['temperature', 'humidity', 'pressure', 'disaster_type']
for col in required_cols:
    if col not in data.columns:
        print(f"Column {col} not found in sensor_data.csv")
        exit()

# Generate a severity label (example logic)
# You can customize this formula as you like
data['severity_score'] = data['temperature'] + (100 - data['humidity'])/2 + (1020 - data['pressure'])
bins = [0, 50, 100, 200]
labels = ['Safe', 'Warning', 'Critical']
data['severity_label'] = pd.cut(data['severity_score'], bins=bins, labels=labels, include_lowest=True)

# Encode disaster type
le_disaster = LabelEncoder()
data['disaster_type_enc'] = le_disaster.fit_transform(data['disaster_type'])

# Features and target
X = data[['temperature', 'humidity', 'pressure', 'disaster_type_enc']]
y = data['severity_label']

# Train-test split (just in case)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "ai_disaster_model.pkl")
print("✅ AI model created successfully as ai_disaster_model.pkl")
