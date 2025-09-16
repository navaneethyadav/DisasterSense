import requests
from config import API_KEY

# Set city name
city = "Bangalore"

# API URL
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

# Fetch data
response = requests.get(url)
data = response.json()

# Print weather details
if data.get("main"):
    print("City:", city)
    print("Temperature:", data["main"]["temp"], "°C")
    print("Humidity:", data["main"]["humidity"], "%")
    print("Weather Condition:", data["weather"][0]["description"])
else:
    print("Error fetching data:", data)
