import pandas as pd
from datetime import datetime
import random
import os

# CSV file path
sensor_file = "data/real_sensor_data.csv"

# Ensure data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Generate random sensor data
row = {
    "temperature": round(random.uniform(20, 40), 1),
    "humidity": round(random.uniform(40, 90), 1),
    "pressure": round(random.uniform(1005, 1020), 1),
    "predicted_disaster": "",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "latitude": round(random.uniform(-90, 90), 4),
    "longitude": round(random.uniform(-180, 180), 4)
}

# Append row to CSV
if os.path.isfile(sensor_file):
    df = pd.read_csv(sensor_file)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
else:
    df = pd.DataFrame([row])

df.to_csv(sensor_file, index=False)
print(f"✅ Added 1 new row to {sensor_file}")
