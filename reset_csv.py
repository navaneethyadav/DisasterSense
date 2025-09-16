import pandas as pd
import os

# CSV path
log_file = "data/prediction_log.csv"

# Ensure data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Overwrite CSV with clean headers
pd.DataFrame(columns=[
    'temperature', 'humidity', 'pressure',
    'predicted_disaster', 'timestamp', 'latitude', 'longitude'
]).to_csv(log_file, index=False)

print("✅ prediction_log.csv has been reset!")
