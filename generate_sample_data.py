import pandas as pd
import random
from datetime import datetime, timedelta
import os

log_file = "data/prediction_log.csv"

if not os.path.exists("data"):
    os.makedirs("data")

rows = []
# Generate 50 sample rows
for i in range(50):
    temp = round(random.uniform(20, 40), 1)
    hum = round(random.uniform(40, 90), 1)
    pres = round(random.uniform(1005, 1020), 1)
    disaster = random.choice(["flood", "wildfire", "landslide", "no disaster"])
    timestamp = datetime.now() - timedelta(minutes=(50-i)*2)
    lat = round(random.uniform(-90, 90), 4)
    lon = round(random.uniform(-180, 180), 4)
    rows.append([temp, hum, pres, disaster, timestamp, lat, lon])

df = pd.DataFrame(rows, columns=[
    'temperature','humidity','pressure',
    'predicted_disaster','timestamp','latitude','longitude'
])

df.to_csv(log_file, index=False)
print("✅ Sample data generated successfully!")
