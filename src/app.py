import random
import os
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest, RandomForestClassifier
load_dotenv()

from authDb import authDb
from users import users

import numpy as np
import pandas as pd
import matplotlib

from flask import (
    Flask, make_response, url_for, render_template, jsonify,
    request, redirect, g
)
from flask_jwt_extended import (
    jwt_required, JWTManager,
    get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
)

from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from opcua import Client
matplotlib.use('Agg')

app = Flask(__name__)
app.register_blueprint(users)

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False  # Set to False in development if not using HTTPS
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie' 
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False 
jwt = JWTManager(app)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def before_request():
    authDb.init_db()

    if request.endpoint in ['users.newUser','users.register', 'users.signin','users.login','users.activateUser','static']:
        return
    try:
        verify_jwt_in_request()
    except:
        # Redirect to login and save the attempted URL
        return redirect(url_for('users.login', next=request.url))
    
@app.route("/")
@jwt_required()
def homepage():  
    current_user = get_jwt_identity() 
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:    
            client.connect()
            idx = 2
            machines_folder = client.get_node(f"ns={idx};s=Machines") 
            machine_nodes = machines_folder.get_children()

            for machine in machine_nodes:
                machine_id = machine.get_child([f"{idx}:MachineID"]) 
                machine_id_value = machine_id.get_value()[0]
                uptime_node = machine.get_child([f"{idx}:Machine_Uptime"]) 
                uptime_value = uptime_node.get_value()
                vibration_node = machine.get_child([f"{idx}:Machine_Vibrations"]) 
                vibration_value = vibration_node.get_value()
                temperature_node = machine.get_child([f"{idx}:Machine_Temperatures"]) 
                temperature_value = temperature_node.get_value()
    finally:
        client.disconnect()

    data = pd.DataFrame({
            'MachineID': machine_id_value,
            'Temperature': temperature_value,
            'Vibration': vibration_value,
            'Uptime': uptime_value
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
    return render_template('home.html', 
                        machine_health_table=table_html,
                        machine_data = machine_data, current_user = current_user)

@app.route("/productionRates")
@jwt_required()
def productionRates():
    # Connect to the OPC UA server
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        idx = 2
        products_folder = client.get_node(f"ns={idx};s=Products") 
        product_nodes = products_folder.get_children()
        labels = []
        data = []
        df = pd.DataFrame()
        for product in product_nodes:
            labels.append(product.get_browse_name().Name)
            rate_node = product.get_child([f"{idx}:ProductRate"]) 
            rate_value = round(random.uniform(rate_node.get_value() / 2, 80),2)
            data.append((rate_value))

            shift_node = product.get_child([f"{idx}:Shift"]) 
            shift_value = shift_node.get_value()
            humidity_node = product.get_child([f"{idx}:Humidity"])
            humidity_value = humidity_node.get_value()
            temperature_node = product.get_child([f"{idx}:Temperature"])
            temperature_value = temperature_node.get_value()
            vibration_node = product.get_child([f"{idx}:Vibration"])
            vibration_value = vibration_node.get_value()

            df['shift'] = shift_value
            df['temperature'] = temperature_value
            df['humidity'] = humidity_value
            df['vibration'] = vibration_value
    
            df['Actual_Rate'] = (
                100 
                - (df['temperature'] * 0.5 + df['humidity'] * 0.2 + df['shift'] * 2) 
                + np.random.normal(0, 5, len(df))  # Match noise to DataFrame size
            )
    finally:        
        client.disconnect()

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        dataset = jsonify({
            'labels': labels,
            'data': data
        })
        return dataset
    else:    
      
        X = df[['shift', 'temperature', 'humidity']]
        y = df['Actual_Rate']
        model = LinearRegression().fit(X, y)
        df['Predicted_Rate'] = model.predict(X)

        coefs = model.coef_
        intercept = model.intercept_
        df['Shift_Impact']    = df['shift'] * coefs[0]
        df['Temp_Impact']     = df['temperature']  * coefs[1]
        df['Humidity_Impact'] = df['humidity'] * coefs[2]  
        df['Intercept'] = intercept
      
        def categorize(v):
            if -1 <= v <= 1:
                return 'Low'
            elif -3 <= v < -1 or 1 < v <= 3:
                return 'Medium'
            else:
                return 'High'

        for feat in ('Shift_Impact', 'Temp_Impact', 'Humidity_Impact'):
            df[f'{feat}_Cat'] = df[feat].apply(categorize)
            del df[feat]
            df[feat.replace("_", " ")] = df.pop(f'{feat}_Cat')
        
        # Summary counts
        # summary = {
        #     feat: df[f'{feat}'].value_counts().to_dict()
        #     for feat in ('Shift Impact', 'Temp Impact', 'Humidity Impact')
        # }

        # Inline‐style mapping for categories
        def style_cat(cell_value):
            if cell_value == 'High':
                return 'background-color: lightcoral;'
            elif cell_value == 'Medium':
                return 'background-color: yellow;'
            else:  # Low
                return 'background-color: lightgreen;'

        # Build Styler and output HTML
        styler = (
            df.style
                .applymap(style_cat, subset=[
                    'Shift Impact',
                    'Temp Impact',
                    'Humidity Impact'
                ])
                .set_table_attributes('class="table table-small"')
                .format(precision=2)
        )
        del df['shift']
        table_html = styler.to_html()
        current_user = get_jwt_identity() 
        return render_template('index.html',table_html=table_html, current_user = current_user)

@app.route("/iotDevices")
@jwt_required()
def iotDevices():
    current_user = get_jwt_identity() 
    return render_template('iotDevices.html', current_user = current_user)

@app.route("/motor")
@jwt_required()
def motorSpeed():
     # Fetch temperature and motor speed data from OPC UA server (simulate if unavailable)
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        idx = 2
        motor = client.get_node(f"ns={idx};s=Motor")
        temperatures = motor.get_child([f"{idx}:Temperatures"]).get_value()
        motor_speeds = motor.get_child([f"{idx}:MotorSpeeds"]).get_value()
    finally:
        client.disconnect()

    # Prepare data for regression
    X = np.array(temperatures).reshape(-1, 1)
    y = motor_speeds

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)
    predicted_speed = model.predict(X)

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        # Return JSON for charting
        return jsonify({
            'labels': temperatures,
            'datasets': [
                {
                    'label': 'Actual Data',
                    'data': motor_speeds,
                    'yAxisID': 'y'
                },
                {
                    'label': 'Learned Trend Line',
                    'data': predicted_speed.tolist(),
                    'yAxisID': 'y1'
                }
            ]
        })
    else:    
        current_user = get_jwt_identity()
        model_eq = f"Speed = {model.coef_[0]:.2f} * Temp + {model.intercept_:.2f}"
        r2 = r2_score(y, predicted_speed)
        r2_text = f"Model Accuracy (R²): {r2:.3f}"

        data_table = pd.DataFrame({
            'Temperature (°C)': np.array(temperatures).flatten(),
            'Actual Speed (RPM)': np.array(motor_speeds).flatten(),
            'Predicted Speed (RPM)': np.array(predicted_speed).flatten()
        })
        table_html = data_table.to_html(classes='table table-striped', index=False)
        return render_template(
            "motorSpeed.html",
            table=table_html,
            model_eq=model_eq,
            r2_text=r2_text,
            current_user=current_user
        )

@app.route("/senser")
@jwt_required()
def senser():
    datasets = []
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        idx = 2
        sensors_folder = client.get_node(f"ns={idx};s=Sensors") 
        sensor_nodes = sensors_folder.get_children() 
        values = [random.uniform(-50, 60), random.uniform(-20, 40),random.uniform(-10, 30)]
        df = pd.DataFrame()
        for j, sensor in enumerate(sensor_nodes):
            signal_node = sensor.get_child([f"{idx}:Signal"]) 
            signals = signal_node.get_value()

            df[f'Senser {j+1}'] = signals
            df[f'Senser {j+1}'] = df[f'Senser {j+1}'].apply(lambda x: x + values[j] * 10)

            data = []
            for i, value in enumerate(signals):
                    value += values[j] * 10
                    s = { 'x': i, 'y': value }
                    data.append(s) 

            datasets.append({
                'label': f'Senser {j+1}',
                'borderWidth': 1,
                'radius': 0,
                'data': data
            }) 

        sensor_data = df.copy()
    
        model = IsolationForest(contamination=0.1).fit(sensor_data)
        df['Anomaly Score'] = model.decision_function(sensor_data)
        df['Anomaly Flag'] = pd.Series(model.predict(sensor_data)).map({1: 'Normal', -1: 'Anomaly'})

        table_html = df.to_html(classes='table table-sm', index=False)
    finally:
        client.disconnect()

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return jsonify(datasets)
    else: 
        access_token = request.cookies.get('access_token_cookie')
        if not access_token:
            return render_template('error.html', msg= "You are not authorized to access this page.")    
        
        current_user = get_jwt_identity()   
        return render_template('senser.html', table=table_html, current_user = current_user)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = make_response(redirect(request.args.get("next") or url_for("homepage")))
    unset_jwt_cookies(response)
    return response, 401

@jwt.unauthorized_loader
def missing_token_callback(err):
    response = make_response(redirect(request.args.get("next") or url_for("homepage")))
    unset_jwt_cookies(response)
    return response, 401

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001)