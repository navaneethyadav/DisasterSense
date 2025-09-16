# dashboard.py

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import random
from datetime import datetime
import requests

# -----------------------------
# Step 1: Initialize data
# -----------------------------
try:
    data = pd.read_csv("data/sensor_data.csv")
except FileNotFoundError:
    data = pd.DataFrame(columns=['temperature','humidity','pressure','disaster_type'])

# Ensure required columns
for col in ['temperature','humidity','pressure','disaster_type']:
    if col not in data.columns:
        data[col] = pd.Series([None]*len(data))

# -----------------------------
# Step 2: EmailJS Setup
# -----------------------------
EMAILJS_SERVICE_ID = "service_107qwwj"
EMAILJS_TEMPLATE_ID = "template_5xp70jt"
EMAILJS_USER_ID = "th0pUdBJgc7NdL_-L"

def send_alert(disaster_type, severity):
    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_USER_ID,
        "template_params": {
            "disaster_type": disaster_type,
            "severity": severity,
            "to_email": "receiver@example.com"  # Replace with your recipient email
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Alert sent for {disaster_type}!")
    else:
        print("Failed to send alert:", response.text)

# -----------------------------
# Step 3: Dash App
# -----------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("DisasterSense Live IoT Dashboard", style={'textAlign':'center','color':'darkblue'}),
    
    # Store for live data
    dcc.Store(id='live-data-store', data=data.to_dict('records')),

    # Dashboard Cards
    html.Div(id='dashboard-cards', style={'display':'flex', 'justifyContent':'space-around', 'marginBottom':'20px'}),

    # Filters
    html.Div([
        html.Label("Select Disaster Type:"),
        dcc.Dropdown(
            id='disaster-type-dropdown',
            options=[
                {'label':'All', 'value':'All'},
                {'label':'Flood','value':'flood'},
                {'label':'Landslide','value':'landslide'},
                {'label':'Wildfire','value':'wildfire'}
            ],
            value='All',
            clearable=False,
            style={'width':'200px'}
        ),
        html.Label("Select Severity Range:"),
        dcc.RangeSlider(
            id='severity-range-slider',
            min=0, max=3000, step=1,
            value=[0,3000],
            marks={0:'0',500:'500',1000:'1000',1500:'1500',2000:'2000',2500:'2500',3000:'3000'},
            tooltip={"placement":"bottom","always_visible":True},
            allowCross=False
        )
    ], style={'display':'flex','gap':'50px','marginBottom':'20px'}),

    # Graphs
    html.Div([
        dcc.Graph(id='temp-humidity-pressure-graph'),
        dcc.Graph(id='disaster-count-graph'),
        dcc.Graph(id='disaster-map')
    ]),

    # Interval for live update every 5 seconds
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0)
])

# -----------------------------
# Step 4: Generate new sensor data
# -----------------------------
def generate_new_sensor_data():
    return {
        'temperature': round(random.uniform(20,40),1),
        'humidity': round(random.uniform(40,90),1),
        'pressure': round(random.uniform(1005,1020),1),
        'disaster_type': random.choice(['flood','landslide','wildfire'])
    }

# -----------------------------
# Step 5: Update live data store
# -----------------------------
@app.callback(
    Output('live-data-store','data'),
    Input('interval-component','n_intervals'),
)
def update_live_data(n):
    global data
    new_row = generate_new_sensor_data()
    data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
    
    # Calculate severity
    severity = new_row['temperature'] + (100-new_row['humidity'])/2 + (1020-new_row['pressure'])
    
    # Send email alert if severity exceeds threshold
    if severity > 120:  # Adjust threshold as needed
        send_alert(new_row['disaster_type'], severity)

    return data.to_dict('records')

# -----------------------------
# Step 6: Dashboard Cards
# -----------------------------
@app.callback(
    Output('dashboard-cards','children'),
    Input('live-data-store','data'),
    Input('disaster-type-dropdown','value'),
    Input('severity-range-slider','value')
)
def update_cards(records, disaster_type, severity_range):
    df = pd.DataFrame(records)
    if df.empty: return []

    df['severity'] = df['temperature'] + (100-df['humidity'])/2 + (1020-df['pressure'])
    
    if disaster_type != 'All':
        df = df[df['disaster_type']==disaster_type]
    df = df[(df['severity']>=severity_range[0]) & (df['severity']<=severity_range[1])]

    latest = df.iloc[-1] if not df.empty else {'temperature':0,'humidity':0}
    total_disasters = len(df)
    disaster_counts = df['disaster_type'].value_counts().to_dict()

    cards = [
        html.Div([
            html.H3("Total Disasters", style={'textAlign':'center'}),
            html.P(f"{total_disasters}", style={'fontSize':'24px','textAlign':'center','color':'darkred'})
        ], style={'border':'2px solid black','padding':'10px','width':'20%','borderRadius':'10px'}),
        html.Div([
            html.H3("Latest Temperature & Humidity", style={'textAlign':'center'}),
            html.P(f"{latest['temperature']}°C / {latest['humidity']}%", style={'fontSize':'20px','textAlign':'center','color':'darkgreen'})
        ], style={'border':'2px solid black','padding':'10px','width':'30%','borderRadius':'10px'}),
        html.Div([
            html.H3("Disaster Counts", style={'textAlign':'center'}),
            html.P(f"Flood: {disaster_counts.get('flood',0)} | Landslide: {disaster_counts.get('landslide',0)} | Wildfire: {disaster_counts.get('wildfire',0)}", style={'fontSize':'18px','textAlign':'center','color':'blue'})
        ], style={'border':'2px solid black','padding':'10px','width':'40%','borderRadius':'10px'})
    ]
    return cards

# -----------------------------
# Step 7: Line Graph
# -----------------------------
@app.callback(
    Output('temp-humidity-pressure-graph','figure'),
    Input('live-data-store','data'),
    Input('disaster-type-dropdown','value'),
    Input('severity-range-slider','value')
)
def update_line_graph(records, disaster_type, severity_range):
    df = pd.DataFrame(records)
    if df.empty: return px.line()
    
    df['severity'] = df['temperature'] + (100-df['humidity'])/2 + (1020-df['pressure'])
    if disaster_type != 'All':
        df = df[df['disaster_type']==disaster_type]
    df = df[(df['severity']>=severity_range[0]) & (df['severity']<=severity_range[1])]

    fig = px.line(df, y=['temperature','humidity','pressure'], title="Temperature, Humidity & Pressure Over Time")
    fig.update_layout(xaxis_title='Time', yaxis_title='Value')
    return fig

# -----------------------------
# Step 8: Bar Graph
# -----------------------------
@app.callback(
    Output('disaster-count-graph','figure'),
    Input('live-data-store','data'),
    Input('disaster-type-dropdown','value'),
    Input('severity-range-slider','value')
)
def update_bar_graph(records, disaster_type, severity_range):
    df = pd.DataFrame(records)
    if df.empty: return px.bar()
    df['severity'] = df['temperature'] + (100-df['humidity'])/2 + (1020-df['pressure'])
    if disaster_type != 'All':
        df = df[df['disaster_type']==disaster_type]
    df = df[(df['severity']>=severity_range[0]) & (df['severity']<=severity_range[1])]

    count = df['disaster_type'].value_counts().reset_index()
    count.columns=['disaster_type','count']
    fig = px.bar(count, x='disaster_type', y='count', color='disaster_type', title="Disaster Counts", text='count')
    return fig

# -----------------------------
# Step 9: Map
# -----------------------------
@app.callback(
    Output('disaster-map','figure'),
    Input('live-data-store','data'),
    Input('disaster-type-dropdown','value'),
    Input('severity-range-slider','value')
)
def update_map(records, disaster_type, severity_range):
    df = pd.DataFrame(records)
    if df.empty: return px.scatter_map()
    df['severity'] = df['temperature'] + (100-df['humidity'])/2 + (1020-df['pressure'])
    if disaster_type != 'All':
        df = df[df['disaster_type']==disaster_type]
    df = df[(df['severity']>=severity_range[0]) & (df['severity']<=severity_range[1])]
    
    df['latitude'] = df.get('latitude', pd.Series([random.uniform(-90,90) for _ in range(len(df))]))
    df['longitude'] = df.get('longitude', pd.Series([random.uniform(-180,180) for _ in range(len(df))]))
    df['marker_size'] = 5 + 20*(df['severity']-df['severity'].min())/(df['severity'].max()-df['severity'].min()+1e-5)
    
    color_map = {'flood':'blue','landslide':'brown','wildfire':'red'}
    fig = px.scatter_map(df, lat='latitude', lon='longitude', color='disaster_type',
                         size='marker_size', size_max=25, color_discrete_map=color_map,
                         hover_data=['temperature','humidity','pressure','severity'], zoom=1, height=400)
    fig.update_layout(map_style='open-street-map', title="Disaster Map")
    return fig

# -----------------------------
# Step 10: Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
