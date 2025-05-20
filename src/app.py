from flask import Flask, url_for ,render_template,jsonify,request
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
import matplotlib
import matplotlib.colors as mcolors
import streamlit as st
from opcua import Client
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import random
matplotlib.use('Agg')

# Generate random temperature and motor speed data
temperature = np.linspace(20, 100, 50)
motor_speed = 5000 - (temperature * 30) + np.random.normal(0, 100, size=50)

# Normalize data
temp_norm = (temperature - temperature.mean()) / temperature.std()
speed_norm = (motor_speed - motor_speed.mean()) / motor_speed.std()

# Step 1: Generate dummy sensor data
def generate_sensor_data():
    np.random.seed(42)
    n = 100
    temperature = np.random.normal(70, 10, n)
    humidity = np.random.normal(50, 15, n)
    vibration = np.random.normal(0.3, 0.1, n)
    age = np.random.randint(50, 500, n)
    signal_loss = 0.1 * temperature + 0.2 * humidity + 30 * vibration + 0.05 * age + np.random.normal(0, 5, n)

    df = pd.DataFrame({
        "Temperature": temperature,
        "Humidity": humidity,
        "Vibration": vibration,
        "Age": age,
        "Signal Loss": signal_loss
    })
    return df

# Step 2: Train model and get feature importances
def analyze_data(df):
    X = df[['Temperature', 'Humidity', 'Vibration', 'Age']]
    y = df['Signal Loss']
    model = RandomForestRegressor()
    model.fit(X, y)

    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False)
    return importance_df

def machine_health():
    # Simulate machine health data
    data = pd.DataFrame({
        'MachineID': [f"M{i:02d}" for i in range(1, 11)],
        'Temperature': np.random.normal(75, 10, 10),
        'Vibration': np.random.normal(0.5, 0.1, 10),
        'Uptime': np.random.uniform(100, 1000, 10)
    })
    data['Failure_Risk'] = np.random.choice([0, 1], size=10)

    X = data[['Temperature', 'Vibration', 'Uptime']]
    y = data['Failure_Risk']
    model = RandomForestClassifier().fit(X, y)
 
    data['Risk_Probability'] = (model.predict_proba(X)[:, 0] * 100).round(2)
    data['Risk_Probability'] = data['Risk_Probability'].astype(str) + '%'
    data['Risk_Probability'] = data['Risk_Probability'].replace('0.0%', '0%')
    data['Risk_Probability'] = data['Risk_Probability'].replace('100.0%', '100%')
    data['Risk_Probability'] = data['Risk_Probability'].replace('nan', '0%')
    data['Failure_Risk'] = data['Failure_Risk'].replace(0, 'No Risk')
    data['Failure_Risk'] = data['Failure_Risk'].replace(1, 'Risk')

    machine_data = data.to_dict()
    table_html = data.to_html(classes='table table-sm', index=False)
    
    return table_html, machine_data

def production_slowdown():
    # 1) Simulate data
    data = pd.DataFrame({
        'Shift': np.random.choice([1, 2, 3], size=10),
        'Temp': np.random.normal(25, 5, 10),
        'Humidity': np.random.normal(50, 10, 10),
    })
    data['Actual_Rate'] = (
        100
        - (data['Temp'] * 0.5 + data['Humidity'] * 0.2 + data['Shift'] * 2)
        + np.random.normal(0, 5, 10)
    )

    # 2) Fit model & get raw impacts
    X = data[['Shift', 'Temp', 'Humidity']]
    y = data['Actual_Rate']
    model = LinearRegression().fit(X, y)
    data['Predicted_Rate'] = model.predict(X)

    coefs = model.coef_
    intercept = model.intercept_
    data['Shift_Impact']    = data['Shift']    * coefs[0]
    data['Temp_Impact']     = data['Temp']     * coefs[1]
    data['Humidity_Impact'] = data['Humidity'] * coefs[2]  
    data['Intercept'] = intercept

    # 3) Turn each impact into Low/Medium/High
    def categorize(v):
        if -1 <= v <= 1:
            return 'Low'
        elif -3 <= v < -1 or 1 < v <= 3:
            return 'Medium'
        else:
            return 'High'

    for feat in ('Shift_Impact', 'Temp_Impact', 'Humidity_Impact'):
        data[f'{feat}_Cat'] = data[feat].apply(categorize)
        del data[feat]
        data[feat.replace("_", " ")] = data.pop(f'{feat}_Cat')
       
    # 5) Summary counts
    summary = {
        feat: data[f'{feat}'].value_counts().to_dict()
        for feat in ('Shift Impact', 'Temp Impact', 'Humidity Impact')
    }

    # 6) Inline‐style mapping for categories
    def style_cat(cell_value):
        if cell_value == 'High':
            return 'background-color: lightcoral;'
        elif cell_value == 'Medium':
            return 'background-color: yellow;'
        else:  # Low
            return 'background-color: lightgreen;'

    # 7) Build Styler and output HTML
    styler = (
        data.style
            .applymap(style_cat, subset=[
                'Shift Impact',
                'Temp Impact',
                'Humidity Impact'
            ])
            .set_table_attributes('class="table table-small"')
            .format(precision=2)
    )
    del data['Shift']
    table_html = styler.to_html()
    return table_html, summary

def sensor_anomaly():
    # Simulate sensor readings with anomalies
    data = pd.DataFrame({
        'Sensor_1': np.random.normal(100, 5, 20),
        'Sensor_2': np.random.normal(200, 20, 20),
        'Sensor_3': np.append(np.random.normal(300, 15, 18), [500, 510])
    })
    sensor_data = data.copy()  # keep raw sensor readings

    model = IsolationForest(contamination=0.1).fit(sensor_data)
    data['Anomaly Score'] = model.decision_function(sensor_data)
    data['Anomaly Flag'] = pd.Series(model.predict(sensor_data)).map({1: 'Normal', -1: 'Anomaly'})

    table_html = data.to_html(classes='table table-sm', index=False)
    # Build summary
    sensor_summary = data.to_dict()
    return table_html, sensor_summary

def impact_to_category(value):
    if -1 <= value <= 1:
        return 'Low'
    elif -3 <= value < -1 or 1 < value <= 3:
        return 'Medium'
    else:
        return 'High'

app = Flask(__name__)

@app.route("/")
def homepage():
    sensor_html, sensor_summary = sensor_anomaly()
    
    st.markdown(sensor_html, unsafe_allow_html=True)
    #production = production_slowdown()
    # Generate table HTML and summary
    table_html, summary_row = production_slowdown()

    # Display HTML table with color coding
    st.markdown(table_html, unsafe_allow_html=True)

    # Optionally, show the summary row for quick insights
    #st.write(summary_row)
    machine_html, machine_data = machine_health()
    return render_template('home.html', 
                        sensor_anomaly_table=sensor_html, 
                        sensor_summary = sensor_summary,
                        production_slowdown_table=table_html,
                        production_slowdown_summary=summary_row,
                        machine_health_table=machine_html,
                        machine_data = machine_data)
  

@app.route("/productionRates")
def productionRates():
    return render_template('index.html')

@app.route("/iotDevices")
def iotDevices():
   return render_template('iotDevices.html')

@app.route("/motor")
def motorSpeed():
    return render_template('motor.html')

@app.route("/senser")
def senser():
    table_html, sensors = sensor_anomaly()
    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        datasets = []
        client = Client("opc.tcp://0.0.0.0:4840/server/")
        try:
            client.connect()
            idx = 2
            sensors_folder = client.get_node(f"ns={idx};s=Sensors") 
            sensor_nodes = sensors_folder.get_children()
            values = [random.uniform(-50, 60), random.uniform(-20, 40),random.uniform(-10, 30)]
            for j, senser in enumerate(sensor_nodes):
                senser_node = senser.get_child([f"{idx}:Signal"]) 
                signals = senser_node.get_value()
                data = []
                for i, value in enumerate(signals):
                        value += values[j] * 10
                        s = { 'x': i, 'y': value }
                        data.append(s) 

                colors = ['brown', 'pink', 'red']
                datasets.append({
                    'label': f'Senser {j+1}',
                    'borderColor': mcolors.CSS4_COLORS[colors[j]],
                    'borderWidth': 1,
                    'radius': 0,
                    'data': data
                }) 
                
        finally:
            client.disconnect()

        return jsonify(datasets)
    else: 
        return render_template('senser.html', table=table_html)

@app.route("/opcua/motors")
def motor():
    # Connect to the OPC UA server
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        idx = 2
        motors_folder = client.get_node(f"ns={idx};s=Mortors") 
       
        motor_nodes = motors_folder.get_children()
        labels = []
        data = []
        Temperatures = []
        speeds = []
        for motor in motor_nodes:
            Temperatures = [round(random.uniform(0, 100),2) for _ in range(100)] #temperature
            rate_node = motor.get_child([f"{idx}:MotorSpeeds"]) 
            speeds = [round(random.uniform(rate_node.get_value() / 2, 8000),0) for _ in range(100)]

        for i,temperature in enumerate(Temperatures):    
            for j, speed in enumerate(speeds):
                if temperature > 55:
                   speed = round(random.uniform(1000, 4000),0)
                else:
                   speed = round(random.uniform(5000, 8000),0)   
                speeds[j] = speed   

        labels = Temperatures
        data = speeds        

    finally:
        client.disconnect()

    dataset = json.dumps({
        'labels': labels,
        'data': data
    })

    return dataset

@app.route("/ai/motorSpeed")
def motorSpeedWithAI():
    _temperature = _motor_speed = []
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        idx = 2
        motor = client.get_node(f"ns={idx};s=Motor")
        _temperature = motor.get_child([f"{idx}:temperatures"]).get_value()
        _motor_speed = motor.get_child([f"{idx}:speeds"]).get_value()
    finally:
        client.disconnect()
    
    _temperature = temperature
    _motor_speed = 5000 - (_temperature * 30) + np.random.normal(0, 100, size=50)
    X = _temperature.reshape(-1, 1)
    y = _motor_speed    

    model = LinearRegression()
    model.fit(X, y)

    predicted_speed = model.predict(X)

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        data = jsonify({
            'labels' : _temperature.tolist(),
            'datasets' : [
                {
                    'label': 'Actual Data',
                    'data' : _motor_speed.tolist(),
                    'yAxisID': 'y'
                },
                {
                    'label': 'Learned Trend Line',
                    'data' : predicted_speed.tolist(),
                    'yAxisID': 'y1'
                }            
            ]
        })
        return data
    else:
        model_eq = f"Speed = {model.coef_[0]:.2f} * Temp + {model.intercept_:.2f}"
        r2 = r2_score(y, predicted_speed)
        r2_text = f"Model Accuracy (R²): {r2:.3f}"

        # Step 5: Create the updated table
        data_table = pd.DataFrame({
            'Temperature (°C)': _temperature,
            'Actual Speed (RPM)': _motor_speed,
            'Predicted Speed (RPM)': predicted_speed
        })

        table_html = data_table.to_html(classes='table table-striped', index=False)
        return render_template("motorSpeed.html", table=table_html, model_eq=model_eq, r2_text=r2_text)

@app.route("/opcua/products")
def products():
    # Connect to the OPC UA server
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        idx = 2
        products_folder = client.get_node(f"ns={idx};s=Products") 
       
        product_nodes = products_folder.get_children()
        labels = []
        data = []
        for product in product_nodes:
            labels.append(product.get_browse_name().Name)
            rate_node = product.get_child([f"{idx}:ProductRate"]) 
            rate_value = round(random.uniform(rate_node.get_value() / 2, 80),2)
            data.append((rate_value))
    finally:
        client.disconnect()

    dataset = jsonify({
        'labels': labels,
        'data': data
    })
    return dataset

@app.route("/opcua/sensors")
def senserTemperature():
    # Connect to the OPC UA server
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        start_time = "08:00"
        idx = 2
        sensors_folder = client.get_node(f"ns={idx};s=Sensors") 
    
        sensor_nodes = sensors_folder.get_children()
        labels = []
        data = []
        #colors = ["#87cefa", "#ff69b4"]
     
        for i,senser in enumerate(sensor_nodes):
            labels = generate_time_list(start_time, 20)
            s = {
                'label': senser.get_browse_name().Name,
                'data': [round(random.uniform(0, 100),2) for _ in range(24)],
               # 'borderColor': colors[i],
               # 'backgroundColor': colors[i]
            }
            
            data.append(s)
    finally:
        client.disconnect()

    dataset = json.dumps({
        'labels': labels,
        'data': data 
        })

    return dataset


def generate_time_list(start_time_str, interval_minutes=15):
    """Generates a list of time strings for 8 hours, with a given interval.

    Args:
        start_time_str: A string representing the start time in HH:MM format (e.g., "09:00").
        interval_minutes: The interval between time entries in minutes.

    Returns:
        A list of time strings in HH:MM format.
    """
    start_time = datetime.datetime.strptime(start_time_str, "%H:%M")
    time_list = []
    for i in range(8 * 60 // interval_minutes + 1): # Calculate total steps for 8 hours
        current_time = start_time + datetime.timedelta(minutes=i * interval_minutes)
        time_list.append(current_time.strftime("%H:%M"))
    return time_list


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)