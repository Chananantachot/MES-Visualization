import random
import os
from dotenv import load_dotenv
import redis
from sklearn.ensemble import IsolationForest, RandomForestClassifier

load_dotenv()
from authDb import authDb
from users import users

import numpy as np
import pandas as pd
import matplotlib

from flask import (
    Flask, Response, json, make_response, send_from_directory, url_for, render_template, jsonify,
    request, redirect, g
)
from flask_jwt_extended import (
    get_jwt, jwt_required, JWTManager,
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
# Initialize Redis connection for caching
try:
    cache = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
    cache.ping()  # Test connection
except redis.ConnectionError:
    cache = None
    print("Warning: Could not connect to Redis at 127.0.0.1:6379. Caching is disabled.")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def before_request():
    authDb.init_db()

    if request.endpoint in ['users.user', 'users.roles','sw','users.newUser','users.register', 'users.signin','users.login','users.activateUser','static']:
        return
    try:
        verify_jwt_in_request()
    except:
        # Redirect to login and save the attempted URL
        return redirect(url_for('users.login', next=request.url))

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/api/machines/download_csv')
@app.route("/api/machines/health")
@app.route("/")
@jwt_required()
def homepage():  
    current_user = get_jwt_identity() 
    datas = None
    csv_data = None
    if cache is not None:
       csv_data = cache.get("machine_csv_data")
       datas = cache.get("machine_data") if cache.exists('machine_data') else []

    if datas and csv_data:
        datas = json.loads(datas)
        csv_data = csv_data
    else:
        machines = []
        client = Client("opc.tcp://0.0.0.0:4840/server/")
        try:    
                client.connect()
                idx = 2
                machines_folder = client.get_node(f"ns={idx};s=Machines") 
                machine_nodes = machines_folder.get_children()

                for machine in machine_nodes:
                    machine_id = machine.get_child([f"{idx}:MachineID"]) 
                    machine_id_value = machine_id.get_value()
                    uptime_node = machine.get_child([f"{idx}:Machine_Uptime"]) 
                    uptime_value = uptime_node.get_value()
                    vibration_node = machine.get_child([f"{idx}:Machine_Vibrations"]) 
                    vibration_value = vibration_node.get_value()
                    temperature_node = machine.get_child([f"{idx}:Machine_Temperatures"]) 
                    temperature_value = temperature_node.get_value()

                    machines.append({
                        'MachineID': machine_id_value,
                        'Temperature': temperature_value,
                        'Vibration': vibration_value,
                        'Uptime': uptime_value,
                        'Failure_Risk': np.random.choice([0, 1], size=10)
                    })
        finally:
            client.disconnect()

        data = pd.DataFrame(machines)
        #data['Failure_Risk'] = np.random.choice([0, 1], size=9)
        for col in ['Temperature', 'Vibration', 'Uptime','Failure_Risk']:
            data[col] = data[col].apply(lambda x: x[random.randint(0,9)] if isinstance(x, (list, tuple, np.ndarray)) else x)

        X = data[['Temperature', 'Vibration', 'Uptime']]
        y = data['Failure_Risk']
        model = RandomForestClassifier().fit(X, y)

        data['Risk_Probability'] = (model.predict_proba(X)[:, 0] * 100).round(2)
        data['Risk_Probability'] = data['Risk_Probability'].astype(float)
        data['Failure_Risk'] = data['Failure_Risk'].replace(1, 'No Risk')
        data['Failure_Risk'] = data['Failure_Risk'].replace(0, 'Risk')

        datas = []
        for _, machine in data.iterrows(): 
            m = {
                'machineID': machine['MachineID'],
                'temperature': round(machine['Temperature'],2),
                'vibration': round(machine['Vibration'],2),
                'uptime': round(machine['Uptime'],2),
                'failureRisk': machine['Failure_Risk'],
                'riskProbability': round(machine['Risk_Probability'])
            }
            datas.append(m)

        csv_data = data.to_csv(index=False)
        if cache is not None:
            cache.set("machine_csv_data", csv_data, ex=60*60)
            cache.set("machine_data", json.dumps(datas), ex=60*60)    

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        if request.path == '/api/machines/download_csv':
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={"Content-disposition":
                        "attachment; filename=senser_data.csv"})
        
        if request.path == '/api/machines/health':  
            return jsonify(datas)    
    else:
        return render_template('home.html',current_user = current_user , data = datas)

@app.route('/productionRates/download_csv')    
@app.route('/productionRates/chart/data')
@app.route('/productionRates/data')
@app.route("/productionRates")
@jwt_required()
def productionRates():
    productions = None
    dataset = None
    csv_data = None
    if cache is not None:
        productions = cache.get("production_rates") 
        dataset = cache.get("production_chart_data") 
        csv_data = cache.get('production_csv')

    if productions and dataset and csv_data:
        print("Using cached data...")
        productions = json.loads(productions)
        dataset = json.loads(dataset)
        csv_data = csv_data
    else:
    # Connect to the OPC UA server
        client = Client("opc.tcp://0.0.0.0:4840/server/")
        try:
            client.connect()
            idx = 2
            products_folder = client.get_node(f"ns={idx};s=Products") 
            product_nodes = products_folder.get_children()
            labels = []
            data = []
            products = []
         
            df = pd.DataFrame()
            for i,product in enumerate(product_nodes):
                product_name = product.get_child([f"{idx}:ProductName"])
                product_name_value = product_name.get_value()
                labels.append(product_name_value)    

                shifts_node = product.get_child([f"{idx}:Shifts"]) 
                shifts_value = shifts_node.get_value()
                shift = random.randint(0, 2)
                rates = shifts_value[shift]    
                data += rates

                humidity_node =  product.get_child([f"{idx}:Humidity"])
                humidity_value = [float(v) for v in humidity_node.get_value()] 
                temperature_node = product.get_child([f"{idx}:Temperature"])
                temperature_value = [float(v) for v in temperature_node.get_value()]  
                vibration_node = product.get_child([f"{idx}:Vibration"])
                vibration_value = [float(v) for v in vibration_node.get_value()] 

                allRates = []
                total_actual_rate = 0
                maximum_rate = 0
                t = temperature_value[random.randint(0,9)]
                h = humidity_value[random.randint(0,9)]
                for s in range(3):
                    allRates += shifts_value[s]
                    if s == shift: 
                        actual_rate = (
                            round(sum(rates),2)
                            - (t * 0.5 + h * 0.2 + s * 2)
                            + np.random.normal(0, 5)
                        )
                    else:    
                        total_actual_rate += (
                                sum(shifts_value[s])
                                - (t * 0.5 + h * 0.2 + s * 2)
                                + np.random.normal(0, 5)
                            )  
                products.append({
                    'name': product_name_value,
                    'rate': round(sum(rates),2),
                    'shift': shift,
                    'temperature': t,
                    'humidity': h,
                    'vibration': vibration_value,
                    'actualRate': actual_rate, 
                    'Predicted_Rate': 0, 
                    'Temp_Impact': '',  # Placeholder for temperature impact
                    'Shift_Impact': '',  # Placeholder for shift impact
                    'Humidity_Impact': '',  # Placeholder for humidity impact
                    'actual_rates':  round(total_actual_rate,2),
                    'maximum_rate' : round(sum(allRates),2),
                    'overallProductionRate' : 0 #overall_production_rate
                })
            df = pd.DataFrame(products)  
  
        finally:        
            client.disconnect()

        for col in ['shift', 'temperature', 'humidity']:
            df[col] = df[col].apply(lambda x: x[0] if isinstance(x, (list, tuple, np.ndarray)) else x)

        X = df[['temperature', 'humidity']]
        y = df['actual_rates']
        model = LinearRegression().fit(X, y)
        df['Predicted_Rates'] = model.predict(X)        
        df['overallProductionRate'] = (df['Predicted_Rates'] / df['maximum_rate']) * 100       


        X = df[['shift', 'temperature', 'humidity']]
        y = df['actualRate']
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

        # Prepare data for JSON response
        productions = []
        for _, row in df.iterrows():
            if row['shift'] == 0:
                _shift = "06:00 AM – 2:00 PM"
            elif row['shift'] == 1:
                _shift = "2:00 PM – 10:00 PM" 
            else:
                _shift = "10:00 PM – 06:00 AM"
            
            production = {  
                'name': row['name'],
                'shift' : _shift,
                'temperature': round(row['temperature'],2),
                'humidity': round(row['humidity'],2),
                'actualRate': round(row['actualRate'],2),
                'predictedRate': round(row['Predicted_Rate'],2),
                'shiftImpact': row['Shift Impact'],
                'tempImpact': row['Temp Impact'],
                'humidityImpact': row['Humidity Impact'],
                'overallProductionRate': round(row['overallProductionRate'])
            }
            productions.append(production)
            
        dataset = {
            'labels': labels,
            'data': data
        }
        csv_data = df.to_csv(index=False)
        if cache is not None:
            cache.set('production_rates', json.dumps(productions), ex=60*60)  # Cache for 1 hour
            cache.set('production_chart_data', json.dumps(dataset), ex=60*60)
            cache.set("production_csv", csv_data ,ex=60*60)  # Cache CSV data for download
            
    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        if request.path == '/productionRates/download_csv':
            # Create a Response with CSV mime type and attachment header
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={"Content-disposition":
                        "attachment; filename=motor_data.csv"})
        elif request.path == '/productionRates/data':
            return jsonify(productions)
        else:    
            # Return JSON for charting
            if request.path == '/productionRates/chart/data':
                return jsonify(dataset)
    else:        
        current_user = get_jwt_identity() 
        return render_template('index.html', datas = productions , current_user = current_user)

@app.route("/iotDevices")
@jwt_required()
def iotDevices():
    current_user = get_jwt_identity() 
    return render_template('iotDevices.html', current_user = current_user)
@app.route('/motor/download_csv')
@app.route('/motor/chart/data')
@app.route('/motor/data')
@app.route("/motor")
@jwt_required()
def motorSpeed():
    dataset = None
    motor_speeds_data = None
    csv_data = None
    anomaly_percentages = None
    if cache is not None:
        csv_data = cache.get("motor_csv") if cache.exists("motor_csv") else None
        motor_speeds_data = cache.get("motor_data") if cache.exists("motor_data") else None
        dataset = cache.get('motor_chart_data') if cache.exists('motor_chart_data') else None
        anomaly_percentages = cache.get('anomaly_percentages') if cache.exists('anomaly_percentages') else None
        model_eq = cache.get('motor_eq') if cache.exists('motor_eq') else None
        r2_text = cache.get('motor_r2') if cache.exists('motor_r2') else None

    if csv_data and motor_speeds_data and dataset and anomaly_percentages:
        print("Using cached data...")
        motor_speeds_data = json.loads(motor_speeds_data)
        anomaly_percentages = json.loads(anomaly_percentages)
        dataset = json.loads(dataset)    
    else:
        # Fetch temperature and motor speed data from OPC UA server (simulate if unavailable)
        anomaly_percentages = []
        df = pd.DataFrame()
        client = Client("opc.tcp://0.0.0.0:4840/server/")
        try:
            client.connect()
            idx = 2
            motor = client.get_node(f"ns={idx};s=Motors")
            motor_nodes = motor.get_children()  # Get all motor nodes
            all_speeds = []
            for j, motor in enumerate(motor_nodes):
                temperatures = motor.get_child([f"{idx}:Temperatures"]).get_value()
                motor_speeds = motor.get_child([f"{idx}:MotorSpeeds"]).get_value()
            
                df[f'Motor {j+1}'] = np.round(temperatures, 2)  
                df[f'Actual Speed {j+1}'] = motor_speeds
                all_speeds += motor_speeds

                col = f'Actual Speed {j+1}'
                total_readings = len(df[col])  # Total data points per sensor
                indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=10)
                rolling_mean = df[col].rolling(window=indexer,min_periods=1).mean()
                rolling_std = df[col].rolling(window=indexer).std().dropna()
                
                lower_bound = rolling_mean - 1.5 * rolling_std  
                upper_bound =rolling_mean + 1.5 * rolling_std  
               
                # Detect anomalies individually per motor
                anomalies = (df[col] < lower_bound) | (df[col] > upper_bound)
                
                # Count anomalies for percentage calculation
                anomaly_percentage = (anomalies.sum() / total_readings) * 100  # Convert to percentage          

                anomaly_percentages.append(round(anomaly_percentage))
        finally:
            client.disconnect()

        df_final = df.copy()

        X = df_final[[col for col in df_final.columns if col.startswith("Motor")]].values
        y = df_final[[col for col in df_final.columns if col.startswith("Actual Speed")]].mean(axis=1).values

        model = LinearRegression()
        model.fit(X, y)

        predicted_speed = model.predict(X)
        df_final['Predicted Speed'] = predicted_speed

        model_eq = f"Speed = {model.coef_[0]:.2f} * Temp + {model.intercept_:.2f}"
        r2 = r2_score(y, df_final['Predicted Speed'])
        r2_text = f"Model Accuracy (R²): {r2:.3f}"
      
        dataset = {
            'labels': temperatures[:10],
            'datasets': [
                {
                    'label': 'Actual Data',
                    'data': all_speeds[:10],
                    'yAxisID': 'y',
                    'type': 'bar',
                    'order': 1
                },
                {
                    'label': 'Learned Trend Line',
                    'data': predicted_speed.tolist()[:10],
                    'yAxisID': 'y1',
                    'order': 0
                }
            ]
        }
        
        motor_speeds_data = df_final.to_dict(orient='records')
        csv_data = df_final.to_csv(index=False)

        if cache is not None:
            cache.set('motor_chart_data', json.dumps(dataset), ex=60*60) 
            cache.set('anomaly_percentages', json.dumps(anomaly_percentages), ex=60*60) 
            
            cache.set("motor_csv", csv_data)  # Cache CSV data for download
            cache.set("motor_data", json.dumps(motor_speeds_data), ex=60*60)  # Cache motor speeds data for 1 hour
            cache.set('motor_eq', model_eq, ex=60*60)  # Cache model equation for 1 hour
            cache.set('motor_r2', r2_text, ex=60*60)

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        # Return JSON for charting

        if request.path == '/motor/download_csv':
            # Create a Response with CSV mime type and attachment header
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={"Content-disposition":
                        "attachment; filename=motor_data.csv"})
        elif request.path == '/motor/data':
            return jsonify(motor_speeds_data)
        else:
            if request.path == '/motor/chart/data':
                return jsonify(dataset)
        
    else:    
        current_user = get_jwt_identity()  
        return render_template(
            "motorSpeed.html",
            model_eq=model_eq,
            r2_text=r2_text,
            current_user=current_user,
            datas = anomaly_percentages
        )

@app.route('/senser/download_csv')
@app.route('/senser/chart/data')
@app.route('/senser/data')
@app.route("/senser")
@jwt_required()
def senser():
    datasets = None
    sensors = None
    csv_data = None
    chart_data = None
    sensor_data = None
    anomaly_percentages = None
    if cache is not None:
        csv_data = cache.get("sensor_csv") if cache.exists("sensor_csv") else None
        sensor_data = cache.get("senser_data") if cache.exists("senser_data") else None
        chart_data = cache.get('senser_chart_data') if cache.exists('senser_chart_data') else None
        anomaly_percentages = cache.get('anomaly_percentages') if cache.exists('anomaly_percentages') else None

    if chart_data and sensor_data and anomaly_percentages:
        sensors = json.loads(sensor_data)
        datasets = json.loads(chart_data)
        anomaly_percentages = json.loads(anomaly_percentages)
        print("Using cacheds data...")     
    else:
        anomaly_percentages = []
        # Fetch sensor data from OPC UA server (simulate if unavailable)
        client = Client("opc.tcp://0.0.0.0:4840/server/")
        try:
            client.connect()
            idx = 2

            sensors_folder = client.get_node(f"ns={idx};s=Sensors") 
            sensor_nodes = sensors_folder.get_children() 

            df = pd.DataFrame()
            datasets = []

            for j, sensor in enumerate(sensor_nodes):
                signal_node = sensor.get_child([f"{idx}:Signal"]) 
                signals = signal_node.get_value()

                df[f'Sensor {j}'] = signals
              
                data = []
                for i, signal in enumerate(signals):
                    data.append({ 'x': i, 'y': signal }) 

                datasets.append({
                    'label': f'Sensor {j+1}',
                    'borderWidth': 1,
                    'radius': 0,
                    'data': data
                }) 
           
            indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=10)
            for sensor in df.columns: 
                total_readings = len(df[sensor])  # Total data points per sensor

                # Calculate rolling mean and std for dynamic thresholding (APPLY ONLY TO SENSOR COLUMN)
                rolling_mean = df[sensor].rolling(window=indexer, min_periods=1).mean()
                rolling_std = df[sensor].rolling(window=indexer).std().dropna()
               
                # Dynamic anomaly detection: Signals deviating beyond rolling mean ± 3*rolling_std
                anomalies = (df[sensor] < rolling_mean - 2*rolling_std) | (df[sensor] > rolling_mean + 2*rolling_std)

                # Count anomalies for percentage calculation
                anomaly_percentage = (anomalies.sum() / total_readings) * 100  # Convert to percentage
                # Store results
                anomaly_percentages.append(round(anomaly_percentage))  

            sensor_data = df.copy()
        
            model = IsolationForest(contamination=0.1).fit(sensor_data)
            df['Anomaly Score'] = model.decision_function(sensor_data)
            df['Anomaly Flag'] = pd.Series(model.predict(sensor_data)).map({1: 'Normal', -1: 'Anomaly'}).tolist()
            df['Anomaly Score'] =  df['Anomaly Score'].round(2).tolist()

            csv_data = df.to_csv(index=False)
            sensors = df.to_dict(orient='records')

            if cache is not None:
                cache.set("sensor_csv", csv_data, ex=60*60)  
                cache.set('senser_data', json.dumps(sensors), ex=60*60)
                cache.set('senser_chart_data', json.dumps(datasets), ex=60*60) 
                cache.set('anomaly_percentages', json.dumps(anomaly_percentages), ex=60*60) 
                
        finally:
            client.disconnect()

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        if request.path == '/senser/download_csv':
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={"Content-disposition":
                        "attachment; filename=senser_data.csv"})
        elif request.path == '/senser/data':
            return jsonify(sensors)
        else:
            if request.path == '/senser/chart/data':
                josn = {
                    'datasets': datasets,
                }
                return jsonify(josn)
    else: 
        access_token = request.cookies.get('access_token_cookie')
        if not access_token:
            return render_template('error.html', msg= "You are not authorized to access this page.")    
        
        current_user = get_jwt_identity()   
        return render_template('senser.html',current_user = current_user, datas=anomaly_percentages)

# Pagination function
def get_page(data, page_number, page_size):
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    return data[start_index:end_index] 

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
   app.run(ssl_context="adhoc", host='0.0.0.0' , port=5000)  # Use SSL context for HTTPS