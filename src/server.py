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
machines_folder = objects.add_folder(f"ns={idx};s=Machines", "Machines")

# Create Machine object and variables
for i in range(1, 10):
    _machine,temperatures,vibrations,uptime = mes_instance.generate_Machine_data()

    machine = machines_folder.add_object(f"ns={idx};s={_machine[0][i]}", _machine[0][i])
    MachineID = machine.add_variable(idx, "MachineID", _machine[0][i])
    MachineID.set_writable()

    Machine_Temperatures = machine.add_variable(idx, "Machine_Temperatures", temperatures)
    Machine_Temperatures.set_writable()

    Machine_Vibrations = machine.add_variable(idx, "Machine_Vibrations", vibrations)
    Machine_Vibrations.set_writable()
    Machine_Uptime = machine.add_variable(idx, "Machine_Uptime", uptime)
    Machine_Uptime.set_writable()

for i in range(1, 8):
# Create Motor object and variables
    speeds, temperatures = mes_instance.generate_MotorSpeed_and_Temperatures()
    motor = motors_folder.add_object(f"ns={idx};s=Motor{i}", f"Motor{i}")
    motor_temperature = motor.add_variable(idx, "Temperatures",temperatures)
    motor_temperature.set_writable()
    motor_speed = motor.add_variable(idx, "MotorSpeeds", speeds)
    motor_speed.set_writable()

# Create Sensor objects and variables
for i in range(1, 6):
    signal,temperatures,humidity,vibration,age = mes_instance.generate_signal_data()

    sensor = sensors_folder.add_object(f"ns={idx};s=Sensor{i}", f"Sensor{i}")
    sensor_temperature = sensor.add_variable(idx, "Temperatures", temperatures)
    sensor_temperature.set_writable()

    sensor_humidity = sensor.add_variable(idx, "Humidity", humidity)
    sensor_humidity.set_writable()

    sensor_vibration = sensor.add_variable(idx, "Vibration", vibration)
    sensor_vibration.set_writable()

    sensor_signal = sensor.add_variable(idx, "Signal", signal.tolist())
    sensor_signal.set_writable()

    sensor_age = sensor.add_variable(idx, "Age", age)

# Create Product objects and variables
products = mes.load_products()
for i,item in enumerate(products):
    product = products_folder.add_object(f"ns={idx};s={item['product_name']}", f"{item['product_name']}")
    product_name = product.add_variable(idx, "ProductName", item['product_name'])
    product_name.set_writable()
    Shifts = product.add_variable(idx, "Shifts", item['shifts'])
    Shifts.set_writable()

    product_temperature = product.add_variable(idx, "Temperature", item['temperature'] )
    product_temperature.set_writable()

    product_humidity = product.add_variable(idx, "Humidity", item['humidity'] )
    product_humidity.set_writable()

    product_vibration = product.add_variable(idx, "Vibration", item['vibration'] )
    product_vibration.set_writable()
try:
    print("Server started. You can connect to opc.tcp://0.0.0.0:4840/server/")
    print("Press Ctrl+C to stop the server...\n")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server...")
finally:
    server.stop()
