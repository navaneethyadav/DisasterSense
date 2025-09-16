import pandas as pd
import random
import os

# Create folder if not exists
if not os.path.exists('data'):
    os.makedirs('data')

# Number of rows to generate
num_rows = 150

# Possible disaster types
disasters = ['flood', 'wildfire', 'landslide']

# Generate random sensor data
data = {
    'temperature': [round(random.uniform(20, 40), 1) for _ in range(num_rows)],
    'humidity': [round(random.uniform(40, 90), 1) for _ in range(num_rows)],
    'pressure': [round(random.uniform(1005, 1020), 1) for _ in range(num_rows)],
    'disaster_type': [random.choice(disasters) for _ in range(num_rows)]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('data/sensor_data.csv', index=False)
print(f"✅ {num_rows} sensor data rows generated and saved to data/sensor_data.csv")
