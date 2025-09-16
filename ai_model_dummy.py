# ai_model_dummy.py
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Generate dummy training data
data = pd.DataFrame({
    'temperature': [20, 25, 30, 35, 40],
    'humidity': [40, 50, 60, 70, 80],
    'pressure': [1005, 1010, 1015, 1020, 1025],
    'severity_label': ['Safe', 'Safe', 'Warning', 'Warning', 'Critical']
})

X = data[['temperature', 'humidity', 'pressure']]
y = data['severity_label']

# Train a simple decision tree
model = DecisionTreeClassifier()
model.fit(X, y)

# Save it
joblib.dump(model, "ai_disaster_model.pkl")
print("Dummy AI model created as ai_disaster_model.pkl")
