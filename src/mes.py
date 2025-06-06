import json
import os
import random
import numpy as np

class mes:
    def generate_Machine_data(self):
        machine = [f"M{i:02d}" for i in range(10)],
        temperatures =[random.uniform(10, 75) for _ in range(10)] 
        vibrations = [random.uniform(0.1, 0.5) for _ in range(10)] 
        uptime = [random.uniform(100, 1000) for _ in range(10)]

        return machine,temperatures,vibrations,uptime

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

        temperatures = [random.uniform(70, 10) for _ in range(100)]  #[0.0] * 7
        humidity = [random.uniform(50, 15) for _ in range(100)]
        vibration = [random.uniform(0.3, 0.1) for _ in range(100)]
        age = [random.randint(50, 500) for _ in range(100)]

        # Generate signal
        signal = trend + noise
        signal = np.clip(signal, 200, 700)  # Clipping to realistic bounds

        return signal,temperatures,humidity,vibration,age

    def load_products():
        data_path = os.path.join("static", "data", "MOCK_DATA.json")
        with open(data_path, "r") as f:
            _data = json.load(f)
            shifts = []
            unique_products = []
            products = []
            for _item in _data['products']:
                pname = _item['title'].strip().lower()
                shifts.append([random.uniform(20,200) for _ in range(10)])
                shifts.append([random.uniform(25,400) for _ in range(10)])
                shifts.append([random.uniform(15,300) for _ in range(10)])
                if pname not in unique_products:
                    unique_products.append(pname)
                    products.append(
                            {  'product_name' : pname,
                               'shifts': shifts,
                                'temperature': [random.uniform(20, 100) for _ in range(10)],
                                'humidity' : [random.uniform(30, 80) for _ in range(10)],
                                'vibration' : [random.uniform(0.1, 0.5) for _ in range(10)]
                            })
        return products  