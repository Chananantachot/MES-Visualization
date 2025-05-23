import random
import os
from dotenv import load_dotenv
load_dotenv()

from authDb import authDb
from mes import mes
from users import users

import numpy as np
import pandas as pd
import matplotlib
import streamlit as st

from flask import (
    Flask, make_response, url_for, render_template, jsonify,
    request, redirect, g
)
from flask_jwt_extended import (
    jwt_required, JWTManager,
    get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
)

from datetime import datetime, timedelta
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
mes = mes()
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

    sensor_html, sensor_summary = mes.sensor_anomaly()
    st.markdown(sensor_html, unsafe_allow_html=True)

    table_html, summary_row = mes.production_slowdown()
    st.markdown(table_html, unsafe_allow_html=True)

    machine_html, machine_data = mes.machine_health()
    return render_template('home.html', 
                        sensor_anomaly_table=sensor_html, 
                        sensor_summary = sensor_summary,
                        production_slowdown_table=table_html,
                        production_slowdown_summary=summary_row,
                        machine_health_table=machine_html,
                        machine_data = machine_data, current_user = current_user)
  
@app.route("/productionRates")
@jwt_required()
def productionRates():
    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
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
    else:    
        current_user = get_jwt_identity() 
        return render_template('index.html', current_user = current_user)

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

    except Exception:
        # Fallback to simulated data if OPC UA fetch fails
        temperatures = mes.temperature 
        motor_speeds = mes.motor_speed 
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
    table_html, _ = mes.sensor_anomaly()
    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        datasets = []
        client = Client("opc.tcp://0.0.0.0:4840/server/")
        try:
            client.connect()
            idx = 2
            sensors_folder = client.get_node(f"ns={idx};s=Sensors") 
            sensor_nodes = sensors_folder.get_children()
            values = [random.uniform(-50, 60), random.uniform(-20, 40),random.uniform(-10, 30)]
            for j, sensor in enumerate(sensor_nodes):
                senser_node = sensor.get_child([f"{idx}:Signal"]) 
                signals = senser_node.get_value()
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
                
        finally:
            client.disconnect()

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