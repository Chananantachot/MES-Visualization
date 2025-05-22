# Fake It Easy – MES Virtualization Platform

**Fake It Easy** is a virtual Manufacturing Execution System (MES) built for learning, simulating, 
and visualizing real-time production processes in a factory setting. This tool offers an interactive dashboard to monitor simulated sensor data, 
production rates, machine behavior, and potential failures — all without needing access to a real production line.

## 🔍 Overview

The app simulates a complete MES environment with:

- **Live production rate tracking**
- **Motor speed and sensor degradation analysis**
- **IoT device simulation**
- **Authentication system with login/register**
- **Alert indicators (e.g., red/blue dots on charts to indicate status)**

It is perfect for engineers, students, or anyone interested in MES/OT/IT systems, predictive maintenance, and digital factory simulation.

## ✨ Features

- 📊 **Production Rate Dashboard** – Visualizes simulated production metrics with anomaly indicators.
- ⚙️ **Sensor Degradation Analysis** – Detects potential sensor failure or wear over time.
- 🚀 **Motor Speed Monitoring** – Compares motor behavior over time to detect inefficiencies.
- 🔐 **Authentication System** – Supports sign-in, registration, and protected dashboard access.
- 🌐 **Modular UI** – Built with a clean, tabbed navigation system for Production, Sensors, Motors, and IoT views.

## 📸 Screenshots

### Production Rate Visualization  
<img width="1140" alt="Screenshot 2568-05-22 at 19 31 44" src="https://github.com/user-attachments/assets/c9ff6722-019e-4c6c-986b-ef2ac80a04c3" />

### Login Page  
<img width="1166" alt="Screenshot 2568-05-22 at 19 33 02" src="https://github.com/user-attachments/assets/8f76edce-e55c-477f-9ee9-438a7ca2e2e5" />

### and mores
<img width="1140" alt="Screenshot 2568-05-22 at 19 32 32" src="https://github.com/user-attachments/assets/847e6848-3fba-454b-b7c3-85c89a3f6e14" />

<img width="1140" alt="Screenshot 2568-05-22 at 19 32 08" src="https://github.com/user-attachments/assets/8fc7bb00-6647-44f4-b06c-d74376bb7349" />

<img width="1140" alt="Screenshot 2568-05-22 at 19 31 18" src="https://github.com/user-attachments/assets/1830f252-201b-4565-bb8f-a666efa6d27e" />

<img width="1140" alt="Screenshot 2568-05-22 at 19 30 55" src="https://github.com/user-attachments/assets/b4600304-37bc-4128-aafc-2d42062cb46e" />

## 🧰 Tech Stack

- **Frontend**: flask/jinjar/javascript 
- **Backend**: Python
- **Data**: Simulated via pandas, NumPy
- **OPC UA**: Prosys Simulation Server
- **AI/ML (optional)**: Scikit-learn or custom logic for alerts
- **Deployment**: Local or cloud-ready,docker

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Chananantachot/MES-Visualization.git
   cd mes-virtualization/src
2. on your termianl -> follow instructions of this link https://flask.palletsprojects.com/en/stable/installation/#create-an-environment 
3. pip install -r requirements.txt
4. flask --app app run --debug & python3 server.py



