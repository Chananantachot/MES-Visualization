import time
import os
import json
from opcua import Server
from mes import mes

# Initialize MES and OPC UA Server
mes_instance = mes()
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/server/")
server.set_server_name("MES OPC UA Server")
server.start()

# Get Objects node and register namespace
objects = server.get_objects_node()
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# Create folders
products_folder = objects.add_folder(f"ns={idx};s=Products", "Products")
sensors_folder = objects.add_folder(f"ns={idx};s=Sensors", "Sensors")
motors_folder = objects.add_folder(f"ns={idx};s=Motors", "Motors")

# Create Motor object and variables
motor = motors_folder.add_object(f"ns={idx};s=Motor", "Motor")
motor_temperature = motor.add_variable(idx, "Temperatures", mes_instance.temperature.tolist())
motor_temperature.set_writable()
motor_speed = motor.add_variable(idx, "Speeds", mes_instance.motor_speed.tolist())
motor_speed.set_writable()

# Create Sensor objects and variables
for i in range(1, 4):
    sensor = sensors_folder.add_object(f"ns={idx};s=Sensor{i}", f"Sensor{i}")
    sensor_temperature = sensor.add_variable(idx, "Temperatures", mes_instance.sensor_temperatures)
    sensor_temperature.set_writable()
    sensor_signal = sensor.add_variable(idx, "Signal", mes_instance.generate_signal_data())
    sensor_signal.set_writable()

# Create Product objects and variables
data_path = os.path.join("static", "data", "MOCK_DATA.json")
with open(data_path, "r") as f:
    data = json.load(f)
    unique_products = {}
    for item in data:
        pname = item['product_name']
        if pname not in unique_products:
            unique_products[pname] = item
    for item in unique_products.values():
        product = products_folder.add_object(idx, item['product_name'])
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
