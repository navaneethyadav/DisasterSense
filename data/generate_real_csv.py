import pandas as pd
from datetime import datetime
import os

# Make sure data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Create some initial data
data = {
    "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(5)],
    "temperature": [28.5, 30.1, 29.4, 27.8, 31.2],
    "humidity": [70, 65, 72, 68, 75],
    "pressure": [1010, 1009, 1012, 1011, 1008],
    "predicted_disaster": ["None", "Flood", "None", "Heatwave", "None"],
    "latitude": [12.9716, 12.9720, 12.9730, 12.9710, 12.9740],
    "longitude": [77.5946, 77.5950, 77.5960, 77.5930, 77.5970]
}

df = pd.DataFrame(data)
df.to_csv("data/real_sensor_data.csv", index=False)
print("✅ real_sensor_data.csv created with sample data!")
