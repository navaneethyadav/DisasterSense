import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

MODEL_PATH = "ai_disaster_model.pkl"

# If the model already exists, skip training
if not os.path.exists(MODEL_PATH):
    # Generate dummy training data (replace with real dataset later if available)
    data = pd.DataFrame({
        "temperature": [25, 30, 35, 40, 22, 28, 38, 45, 20, 27],
        "humidity": [70, 60, 50, 40, 80, 65, 55, 35, 75, 68],
        "pressure": [1015, 1010, 1008, 1005, 1020, 1012, 1007, 1003, 1018, 1011],
        "disaster_type": ["flood", "flood", "wildfire", "wildfire", "landslide", "flood", "wildfire", "wildfire", "landslide", "flood"],
        "severity_label": ["Safe", "Warning", "Critical", "Critical", "Safe", "Warning", "Critical", "Critical", "Safe", "Warning"]
    })

    # Features and target
    X = data[["temperature", "humidity", "pressure"]]
    y = data["severity_label"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Save the model
    joblib.dump(clf, MODEL_PATH)
    print("AI Model trained and saved.")
else:
    print("Model already exists.")
