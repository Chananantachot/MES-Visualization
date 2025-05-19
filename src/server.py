import time
from opcua import Server
import numpy as np
import json
import os

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/server/")
server.set_server_name("MES OPC UA Server")
server.start()

# get Objects node, this is where we should put our nodes
objects = server.get_objects_node()
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# Create Products folder
products_folder = objects.add_folder(f"ns={idx};s=Products", "Products")
# Create Senser folder
sensers_folder = objects.add_folder(f"ns={idx};s=Sensors", "Sensors")
# Create Motor folder
motor_folder = objects.add_folder(f"ns={idx};s=Motors", "Motors")

# Craate Motor object
mortor = motor_folder.add_object(f"ns={idx};s=Motor", "Motor")
temperature = np.linspace(20, 100, 50).tolist()
motor_temperature = mortor.add_variable(idx, "temperature", temperature)
motor_temperature.set_writable()
motor_speed = mortor.add_variable(idx, "speed",5000 - (temperature * 30) + np.random.normal(0, 100, size=50).tolist())
motor_speed.set_writable()

# Craate Senser object
for i in range(1, 3):
    sensor = sensers_folder.add_object(f"ns={idx};s=Sensor{i}", f"Sensor{i}")
    sensor_temperature = sensor.add_variable(idx, "Temperatures", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    sensor_temperature.set_writable()
    
# Craate Production Rates object
path = os.path.join("static", "data", "MOCK_DATA.json")
with open(path, "r") as f:
    data = json.load(f)
    
    unique_entries = {}
    for item in data:
        if item['product_name'] not in unique_entries:
            unique_entries[item['product_name']] = item
    
    for item in unique_entries.values():
        product = products_folder.add_object(f"ns={idx};s={item['product_name']}", item['product_name'])
        product_rate = product.add_variable(idx, "ProductRate", item['productRate'])
        product_rate.set_writable()

try:
    print("Server started. You can connect to opc.tcp://0.0.0.0:4840/server/")
    print("Press Ctrl+C to stop the server...\n")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server...")
finally:
    server.stop()