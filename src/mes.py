import json
import os
import random
import numpy as np

class mes:
    def __init__(self):

        # Define parameters
        # time_steps = 100  # Number of readings
        # base_speed = 5000  # Typical motor speed (RPM)
        # _std = np.random.uniform(5, 25)
        # fluctuation = np.random.normal(0, _std, time_steps)  # Small natural speed variations
        # anomaly_spikes = np.random.choice([0, -100, +150], size=time_steps, p=[0.98, 0.01, 0.01])  # Occasional faults

        # # Generate motor speed signal
        # motor_speed = base_speed + fluctuation + anomaly_spikes
        # self.motor_temperatures = [round(random.uniform(0, 100),2) for _ in range(100)]
        # self.motor_speed = motor_speed.tolist()

        # self.motor_temperatures = [round(random.uniform(0, 100),2) for _ in range(100)]
        # rates = [5000 - (temp * 30) + np.random.normal(0, 100) for temp in self.motor_temperatures]
        # self.motor_speed = [round(random.uniform(rate / 2, 8000), 0) for rate in rates]

        self.sensor_temperatures = [random.uniform(70, 10) for _ in range(100)]  #[0.0] * 7
        self.sensor_humidity = [random.uniform(50, 15) for _ in range(100)]
        self.sensor_vibration = [random.uniform(0.3, 0.1) for _ in range(100)]
        self.sensor_age = [random.randint(50, 500) for _ in range(100)]
        self.sensor_signal_loss = [0.1 * temp + 0.2 * hum + 30 * vib + 0.05 * age + random.normalvariate(0, 5) 
                                   for temp, hum, vib, age in zip(self.sensor_temperatures, self.sensor_humidity, 
                                                                  self.sensor_vibration, self.sensor_age)] 
        self.MachineID = [f"M{i:02d}" for i in range(10)],
        self.Machine_Temperatures =[random.uniform(10, 75) for _ in range(10)] 
        self.Machine_Vibrations = [random.uniform(0.1, 0.5) for _ in range(10)] 
        self.Machine_Uptime = [random.uniform(100, 1000) for _ in range(10)]

        self.production_temperature = [random.uniform(20, 100) for _ in range(10)]
        self.production_humidity = [random.uniform(30, 80) for _ in range(10)]
        self.production_vibration = [random.uniform(0.1, 0.5) for _ in range(10)]
        self.production_shift = np.random.choice([1, 2, 3], size=10).tolist() 

    def generate_MotorSpeed_and_Temperatures(self):
        motor_temperatures = [round(random.uniform(0, 100),2) for _ in range(100)]
        rates = [5000 - (temp * 30) + np.random.normal(0, 100) for temp in motor_temperatures]
        motor_speed = [round(random.uniform(rate / 2, 8000), 0) for rate in rates]
        return motor_speed , motor_temperatures

    def generate_signal_data(self):
        # Define parameters
        mean = random.uniform(200, 700)  # Baseline mean value
        std = random.uniform(20, 50)  # Standard deviation
        num_samples = 980  # Data points
        trend = np.linspace(mean - 20, mean + 20, num_samples)  # Simulating slow drift
        noise = np.random.normal(0, std, num_samples)  # Gaussian noise

        # Generate signal
        signal = trend + noise
        signal = np.clip(signal, 200, 700)  # Clipping to realistic bounds

        return signal

    def load_products():
        data_path = os.path.join("static", "data", "MOCK_DATA.json")
        with open(data_path, "r") as f:
            _data = json.load(f)
            shifts = []
            for _ in range(3):
                rates = [random.uniform(20,200) for _ in range(8)]
                shifts.append(rates)      

            unique_products = []
            products = []
            for _item in _data['products']:
                pname = _item['title'].strip().lower()
                if pname not in unique_products:
                    unique_products.append(pname)
                    products.append({ 'product_name' : pname, 'shifts': shifts })
        return products  