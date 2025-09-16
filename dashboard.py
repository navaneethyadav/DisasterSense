import os
import random
import threading
import requests
import pandas as pd
import joblib
from dash import Dash, dcc, html, Input, Output
from dotenv import load_dotenv
import plotly.express as px

# Load environment variables
load_dotenv()
EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID")
EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID")
EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT_EMAIL", "test@example.com")

# Load AI model and label encoder
MODEL_FILE = "ai_disaster_model.pkl"
ENCODER_FILE = "label_encoder.pkl"

if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE):
    raise FileNotFoundError("AI model or label encoder not found. Run train_ai_model.py first.")

ai_model = joblib.load(MODEL_FILE)
label_encoder = joblib.load(ENCODER_FILE)

# Load initial sensor data
try:
    data = pd.read_csv("data/sensor_data.csv")
except FileNotFoundError:
    data = pd.DataFrame(columns=['temperature', 'humidity', 'pressure', 'disaster_type'])

for col in ['temperature', 'humidity', 'pressure', 'disaster_type']:
    if col not in data.columns:
        data[col] = pd.Series([0]*len(data))

# Initialize Dash
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("DisasterSense Live IoT Dashboard", style={'textAlign': 'center', 'color': 'darkblue'}),
    dcc.Store(id='store-live-data', data=data.to_dict('records')),
    html.Div(id='cards-dashboard', style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),
    html.Div([
        html.Div([
            html.Label("Select Disaster Type:"),
            dcc.Dropdown(
                id='dropdown-disaster-type',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Flood', 'value': 'flood'},
                    {'label': 'Landslide', 'value': 'landslide'},
                    {'label': 'Wildfire', 'value': 'wildfire'}
                ],
                value='All',
                clearable=False,
                style={'width': '200px'}
            )
        ]),
        html.Div([
            html.Label("Select Severity Range:"),
            dcc.RangeSlider(
                id='slider-severity-range',
                min=0, max=2, step=1,
                value=[0, 2],
                marks={0: 'Safe', 1: 'Warning', 2: 'Critical'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginLeft': '50px'})
    ], style={'display': 'flex', 'gap': '50px', 'marginBottom': '20px'}),
    dcc.Graph(id='graph-temp-humidity-pressure'),
    dcc.Graph(id='graph-disaster-count'),
    dcc.Graph(id='graph-disaster-map'),
    dcc.Interval(id='interval-update', interval=5*1000, n_intervals=0)
])

# Generate new sensor data
def generate_new_sensor_data():
    return {
        'temperature': round(random.uniform(20, 40), 1),
        'humidity': round(random.uniform(40, 90), 1),
        'pressure': round(random.uniform(1005, 1020), 1),
        'disaster_type': random.choice(['flood', 'landslide', 'wildfire'])
    }

# Predict severity
def predict_severity(sensor_row):
    features = [[sensor_row['temperature'], sensor_row['humidity'], sensor_row['pressure']]]
    pred_encoded = ai_model.predict(features)[0]
    severity = label_encoder.inverse_transform([pred_encoded])[0]
    return severity

# Send email alert
def send_email_alert(sensor_row):
    severity = sensor_row.get('severity', 'Safe')
    if severity == 'Safe':
        return
    if not EMAILJS_SERVICE_ID or not EMAILJS_TEMPLATE_ID or not EMAILJS_PUBLIC_KEY:
        print("EmailJS environment variables not set")
        return
    try:
        payload = {
            "service_id": EMAILJS_SERVICE_ID,
            "template_id": EMAILJS_TEMPLATE_ID,
            "user_id": EMAILJS_PUBLIC_KEY,
            "template_params": {
                "disaster_type": sensor_row['disaster_type'],
                "temperature": sensor_row['temperature'],
                "humidity": sensor_row['humidity'],
                "pressure": sensor_row['pressure'],
                "severity": sensor_row['severity'],
                "to_email": ALERT_RECIPIENT
            }
        }
        requests.post("https://api.emailjs.com/api/v1.0/email/send", json=payload)
    except Exception as e:
        print("Email alert failed:", e)

# Update live data
@app.callback(
    Output('store-live-data', 'data'),
    Input('interval-update', 'n_intervals')
)
def update_live_data(n):
    global data
    new_row = generate_new_sensor_data()
    new_row['severity'] = predict_severity(new_row)
    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
    if len(data) > 500:
        data = data.iloc[-500:]
    threading.Thread(target=send_email_alert, args=(new_row,), daemon=True).start()
    return data.to_dict('records')

# Dashboard cards
@app.callback(
    Output('cards-dashboard', 'children'),
    Input('store-live-data', 'data'),
    Input('dropdown-disaster-type', 'value')
)
def update_cards(records, disaster_type):
    df = pd.DataFrame(records)
    if df.empty:
        return []

    if disaster_type != 'All':
        df = df[df['disaster_type'] == disaster_type]

    latest = df.iloc[-1] if not df.empty else {'temperature': 0, 'humidity': 0, 'severity': 'Safe'}
    total_disasters = len(df)
    counts = df['disaster_type'].value_counts().to_dict()
    severity_counts = df['severity'].value_counts().to_dict()

    return [
        html.Div([
            html.H3("Total Disasters", style={'textAlign': 'center'}),
            html.P(str(total_disasters), style={'fontSize': '24px', 'textAlign': 'center', 'color': 'darkred'})
        ], style={'border': '2px solid black', 'padding': '10px', 'width': '20%', 'borderRadius': '10px'}),
        html.Div([
            html.H3("Latest Reading", style={'textAlign': 'center'}),
            html.P(f"{latest['temperature']}°C / {latest['humidity']}% | Severity: {latest['severity']}",
                   style={'fontSize': '18px', 'textAlign': 'center', 'color': 'darkgreen'})
        ], style={'border': '2px solid black', 'padding': '10px', 'width': '30%', 'borderRadius': '10px'}),
        html.Div([
            html.H3("Disaster Counts", style={'textAlign': 'center'}),
            html.P(f"Flood: {counts.get('flood',0)} | Landslide: {counts.get('landslide',0)} | Wildfire: {counts.get('wildfire',0)}",
                   style={'fontSize': '18px', 'textAlign': 'center', 'color': 'blue'}),
            html.P(f"Safe: {severity_counts.get('Safe',0)} | Warning: {severity_counts.get('Warning',0)} | Critical: {severity_counts.get('Critical',0)}",
                   style={'fontSize': '16px', 'textAlign': 'center', 'color': 'purple'})
        ], style={'border': '2px solid black', 'padding': '10px', 'width': '40%', 'borderRadius': '10px'})
    ]

# Line graph
@app.callback(
    Output('graph-temp-humidity-pressure', 'figure'),
    Input('store-live-data', 'data'),
    Input('dropdown-disaster-type', 'value')
)
def update_line_graph(records, disaster_type):
    df = pd.DataFrame(records)
    if df.empty:
        return px.line()

    if disaster_type != 'All':
        df = df[df['disaster_type'] == disaster_type]

    fig = px.line(df, y=['temperature','humidity','pressure'], title="Temperature, Humidity & Pressure Over Time")
    return fig

# Bar graph
@app.callback(
    Output('graph-disaster-count', 'figure'),
    Input('store-live-data', 'data'),
    Input('dropdown-disaster-type', 'value')
)
def update_bar_graph(records, disaster_type):
    df = pd.DataFrame(records)
    if df.empty:
        return px.bar()

    if disaster_type != 'All':
        df = df[df['disaster_type'] == disaster_type]

    counts = df['disaster_type'].value_counts().reset_index()
    counts.columns = ['disaster_type','count']
    fig = px.bar(counts, x='disaster_type', y='count', color='disaster_type', text='count', title="Disaster Counts")
    return fig

# Map graph
@app.callback(
    Output('graph-disaster-map', 'figure'),
    Input('store-live-data', 'data'),
    Input('dropdown-disaster-type', 'value')
)
def update_map(records, disaster_type):
    df = pd.DataFrame(records)
    if df.empty:
        return px.scatter_geo()

    if disaster_type != 'All':
        df = df[df['disaster_type'] == disaster_type]

    df['lat'] = [12.9 + random.uniform(-0.1,0.1) for _ in range(len(df))]
    df['lon'] = [77.6 + random.uniform(-0.1,0.1) for _ in range(len(df))]

    fig = px.scatter_geo(df, lat='lat', lon='lon', color='disaster_type',
                         size=df['temperature'], title="Disaster Locations", projection="natural earth")
    return fig

# Run server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=True)
