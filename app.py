from flask import Flask, url_for ,render_template
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib
from opcua import Client
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import json
import random

matplotlib.use('Agg')
#data_table.to_parquet("large_dataset_results.parquet")

# Generate random temperature and motor speed data
temperature = np.linspace(20, 100, 50)
motor_speed = 5000 - (temperature * 30) + np.random.normal(0, 100, size=50)

# Normalize data
temp_norm = (temperature - temperature.mean()) / temperature.std()
speed_norm = (motor_speed - motor_speed.mean()) / motor_speed.std()

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template('home.html')

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
    return render_template('senser.html')

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
    # Step 1: Reshape your inputs (sklearn expects 2D array)
    X = temperature.reshape(-1, 1)
    y = motor_speed

    # Step 2: Fit the model
    model = LinearRegression()
    model.fit(X, y)

    # Step 3: Get predicted values
    predicted_speed = model.predict(X)
    # Model insights
    model_eq = f"Speed = {model.coef_[0]:.2f} * Temp + {model.intercept_:.2f}"
    r2 = r2_score(y, predicted_speed)
    r2_text = f"Model Accuracy (R²): {r2:.3f}"

    # Step 4: Plot the result
    plt.scatter(temperature, motor_speed, label='Actual Data', color='blue')
    plt.plot(temperature, predicted_speed, label='Learned Trend Line', color='green')  # AI-based line
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Motor Speed (RPM)')
    plt.title('Motor Speed vs Temperature (AI Model)')
    plt.legend()
    plt.savefig("static/graph.png")
    plt.close()

    # Step 5: Create the updated table
    data_table = pd.DataFrame({
        'Temperature (°C)': temperature,
        'Actual Speed (RPM)': motor_speed,
        'Predicted Speed (RPM)': predicted_speed
    })

     # Convert the table to HTML
    table_html = data_table.to_html(classes='table table-striped', index=False)
    graph_url = url_for('static', filename='graph.png')
    # Render the HTML template with the graph and table
    return render_template("motorSpeed.html", table=table_html, graph_url=graph_url,
                       model_eq=model_eq, r2_text=r2_text)


# def motorSpeedWithAI():
#     # Create and save the graph
#     plt.scatter(temperature, motor_speed, label='Actual Data', color='blue')
#     plt.plot(temperature, 5000 - temperature * 30, label='Predicted Line', color='red')  # Example trend line
#     plt.xlabel('Temperature (°C)')
#     plt.ylabel('Motor Speed (RPM)')
#     plt.title('Motor Speed vs Temperature')
#     plt.legend()
#     plt.savefig("static/graph.png")  # Save graph to 'static' folder
#     plt.close()

#     # Create table with pandas
#     predicted_speed = 5000 - (temperature * 30)  # Example predictions
#     data_table = pd.DataFrame({
#         'Temperature (°C)': temperature,
#         'Actual Speed (RPM)': motor_speed,
#         'Predicted Speed (RPM)': predicted_speed
#     })

#     # Convert the table to HTML
#     table_html = data_table.to_html(classes='table table-striped', index=False)
#     graph_url = url_for('static', filename='graph.png')
#     # Render the HTML template with the graph and table
#     return render_template("motorSpeed.html", table=table_html, graph_url=graph_url)


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

    dataset = json.dumps({
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
   app.run(debug=True, threaded=False)