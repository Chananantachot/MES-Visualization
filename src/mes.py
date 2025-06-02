import json
import os
import random
import numpy as np

class mes:
    def __init__(self):
        #temperature = np.linspace(20, 100, 50)
        self.motor_temperatures = [round(random.uniform(0, 100),2) for _ in range(100)]
        rates = [5000 - (temp * 30) + np.random.normal(0, 100) for temp in self.motor_temperatures]
        
        self.motor_speed = [round(random.uniform(rate / 2, 8000), 0) for rate in rates]
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

    def generate_signal_data(self):
        mean, std, tail = random.uniform(200, 700), random.uniform(20, 50), [200, 300]
        signal_data = np.random.normal(mean, std, 980)
        signal_data = np.append(signal_data, tail)
        signal_data = np.array(signal_data, dtype=float).flatten()
        signal_data = [round(float(x), 2) for x in signal_data]
        return signal_data

    @staticmethod
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