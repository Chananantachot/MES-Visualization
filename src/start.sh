#!/bin/bash

echo "🔧 Activating virtual environment..."
. .venv/bin/activate

echo "🛑 Killing processes on ports 6379, 5000, 4840..."
kill -9 $(lsof -ti:6379) 2>/dev/null
kill -9 $(lsof -ti:5000) 2>/dev/null
kill -9 $(lsof -ti:4840) 2>/dev/null

echo "🚀 Starting Redis..."
redis-server &

sleep 1

echo "🧹 Flushing Redis..."
redis-cli FLUSHALL

echo "📡 Starting OPC UA server..."
python server.py &

echo "🌐 Setting Flask env for auto-reload..."
export FLASK_APP=app.py          # update with your actual file
export FLASK_ENV=development     # auto-reload and debug mode

echo "🌐 Starting Flask app with auto-reload..."
flask run --cert=cert.pem --key=key.pem
