#!/bin/bash
# Start the OPC UA server in the background
python server.py &

# Start the Flask app
python app.py
