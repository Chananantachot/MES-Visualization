⬅️➡️ MES (Manufacturing Execution System)
    -  Knows about machine status: temperature, vibration, uptime, etc.

⬅️➡️ OPC UA Server
    - Acts as the centralized "data broker"
    - Stores live machine/sensor data
    - Exposes data via standard OPC UA protocol

    ,,,code 
    from opcua import Server
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
    ....

# Create folders
products_folder = objects.add_folder(f"ns={idx};s=Products", "Products")

⬅️➡️ OPC UA Client
    - Fetches or monitors data from the OPC UA server
    - Can be any service: backend, Raspberry Pi, script, etc.

⬅️➡️ Web UI / Machine Learning / Dashboards
    - Visualizes real-time & historical data
    - Adds analytics like anomaly detection, predictions, etc.
