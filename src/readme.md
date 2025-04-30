⬅️➡️ MES (Manufacturing Execution System)
    -  Knows about machine status: temperature, vibration, uptime, etc.

⬅️➡️ OPC UA Server
    - Acts as the centralized "data broker"
    - Stores live machine/sensor data
    - Exposes data via standard OPC UA protocol

⬅️➡️ OPC UA Client
    - Fetches or monitors data from the OPC UA server
    - Can be any service: backend, Raspberry Pi, script, etc.

⬅️➡️ Web UI / Machine Learning / Dashboards
    - Visualizes real-time & historical data
    - Adds analytics like anomaly detection, predictions, etc.