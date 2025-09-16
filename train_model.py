# DisasterSense AI Model Training with Real-Time Prediction and Model Saving

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# -------------------------
# Step 1: Load Sensor Data
# -------------------------
try:
    data = pd.read_csv("data/sensor_data.csv")
    print("✅ CSV loaded successfully with delimiter ','")
except Exception as e:
    print("❌ Failed to load CSV:", e)
    exit()

# -------------------------
# Step 2: Check columns
# -------------------------
print("Columns in CSV:", data.columns)

# -------------------------
# Step 3: Prepare Features and Target
# -------------------------
if 'disaster_type' not in data.columns:
    print("❌ 'disaster_type' column not found in CSV.")
    exit()

X = data[['temperature', 'humidity', 'pressure']]
y = data['disaster_type']

# -------------------------
# Step 4: Split into Train and Test sets
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("✅ Data split into train and test sets.")

# -------------------------
# Step 5: Scale Features
# -------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✅ Features scaled.")

# -------------------------
# Step 6: Train Model
# -------------------------
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train_scaled, y_train)
print("✅ Model trained successfully.")

# -------------------------
# Step 7: Evaluate Model
# -------------------------
y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy*100:.2f}%")
print("Classification Report:\n", report)

# -------------------------
# Step 8: Save Model and Scaler
# -------------------------
if not os.path.exists("data"):
    os.makedirs("data")

with open("data/disaster_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("data/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
print("✅ Model and scaler saved for dashboard use.")

# -------------------------
# Step 9: Real-Time Prediction
# -------------------------
print("\n🚨 Disaster Prediction (Enter sensor values)")
print("Type 'q' or 'exit' at any time to quit.\n")

while True:
    try:
        temp_input = input("Temperature (°C): ")
        if temp_input.lower() in ['q', 'exit']:
            break
        temp = float(temp_input)

        hum_input = input("Humidity (%): ")
        if hum_input.lower() in ['q', 'exit']:
            break
        hum = float(hum_input)

        pres_input = input("Pressure (hPa): ")
        if pres_input.lower() in ['q', 'exit']:
            break
        pres = float(pres_input)

        # Scale input using DataFrame
        scaled_input = scaler.transform(pd.DataFrame(
            [[temp, hum, pres]],
            columns=['temperature', 'humidity', 'pressure']
        ))

        # Predict disaster
        prediction = model.predict(scaled_input)[0]
        print(f"⚡ Predicted Disaster: {prediction}\n")

    except ValueError:
        print("❌ Invalid input. Please enter numeric values or 'q' to quit.\n")
    except KeyboardInterrupt:
        print("\n🛑 Exiting real-time prediction.")
        break

print("🛑 DisasterSense session ended.")
