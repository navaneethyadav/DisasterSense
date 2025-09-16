# data/auto_append.py
import pandas as pd
import random
import os
import time
from datetime import datetime
import argparse
import signal
import sys

stop_requested = False
def handle_signal(sig, frame):
    global stop_requested
    stop_requested = True
    print("\n🛑 Stop requested. Exiting...")

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def make_row():
    return {
        "temperature": round(random.uniform(20, 40), 1),
        "humidity": round(random.uniform(40, 90), 1),
        "pressure": round(random.uniform(1005, 1020), 1),
        "predicted_disaster": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latitude": round(random.uniform(-90, 90), 4),
        "longitude": round(random.uniform(-180, 180), 4)
    }

def append_row(sensor_file, row):
    df_row = pd.DataFrame([row])
    # If file exists and has header, append without header; else create with header
    if os.path.isfile(sensor_file) and os.path.getsize(sensor_file) > 0:
        df_row.to_csv(sensor_file, mode='a', header=False, index=False)
    else:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(sensor_file), exist_ok=True)
        df_row.to_csv(sensor_file, mode='w', header=True, index=False)

def main():
    parser = argparse.ArgumentParser(description="Auto-append sensor rows to CSV")
    parser.add_argument("--file", "-f", default="data/real_sensor_data.csv", help="Sensor CSV path")
    parser.add_argument("--interval", "-i", type=float, default=5.0, help="Seconds between rows (default 5s)")
    parser.add_argument("--count", "-c", type=int, default=0, help="Number of rows to append (0 = infinite)")
    args = parser.parse_args()

    sensor_file = args.file
    interval = max(0.1, args.interval)
    count = args.count

    print(f"📥 Appending to: {sensor_file}")
    print(f"⏱ Interval: {interval}s, Count: {'infinite' if count==0 else count}")
    i = 0
    try:
        while not stop_requested:
            if count != 0 and i >= count:
                break
            row = make_row()
            try:
                append_row(sensor_file, row)
                print(f"✅ [{i+1}] {row['timestamp']}  Temp={row['temperature']}C Hum={row['humidity']}% Pres={row['pressure']}hPa")
            except Exception as e:
                print("❌ Error writing to CSV:", e)
            i += 1
            # Sleep but break early if stop_requested
            sleep_remaining = interval
            while sleep_remaining > 0 and not stop_requested:
                time.sleep(min(0.5, sleep_remaining))
                sleep_remaining -= 0.5
    except Exception as e:
        print("❌ Unexpected error:", e)
    finally:
        print("🟢 auto_append stopped. Total rows appended:", i)

if __name__ == "__main__":
    main()
