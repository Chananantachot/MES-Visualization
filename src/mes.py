import random
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression

class mes:
    def __init__(self):
        temperature = np.linspace(20, 100, 50)
        motor_speed = 5000 - (temperature * 30) + np.random.normal(0, 100, size=50)
       
        self.temperature = temperature
        self.motor_speed = motor_speed
        self.sensor_temperatures = [0.0] * 7
        self.temp_norm = (temperature - temperature.mean()) / temperature.std()
        self.speed_norm = (motor_speed - motor_speed.mean()) / motor_speed.std()
       
    def generate_signal_data(self):
        mean, std, tail = random.uniform(200, 700), random.uniform(20, 50), [200, 300]
        signal_data = np.random.normal(mean, std, 980)
        signal_data = np.append(signal_data, tail)
        return signal_data.tolist() 
      
    def generate_sensor_data(self):
        np.random.seed(42)
        n = 100
        temperature = np.random.normal(70, 10, n)
        humidity = np.random.normal(50, 15, n)
        vibration = np.random.normal(0.3, 0.1, n)
        age = np.random.randint(50, 500, n)
        signal_loss = 0.1 * temperature + 0.2 * humidity + 30 * vibration + 0.05 * age + np.random.normal(0, 5, n)

        df = pd.DataFrame({
            "Temperature": temperature,
            "Humidity": humidity,
            "Vibration": vibration,
            "Age": age,
            "Signal Loss": signal_loss
        })
        return df

    def analyze_data(df):
        X = df[['Temperature', 'Humidity', 'Vibration', 'Age']]
        y = df['Signal Loss']
        model = RandomForestRegressor()
        model.fit(X, y)

        importances = model.feature_importances_
        importance_df = pd.DataFrame({
            "Feature": X.columns,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False)
        return importance_df

    def machine_health(self):
    # Simulate machine health data
        data = pd.DataFrame({
            'MachineID': [f"M{i:02d}" for i in range(1, 11)],
            'Temperature': np.random.normal(75, 10, 10),
            'Vibration': np.random.normal(0.5, 0.1, 10),
            'Uptime': np.random.uniform(100, 1000, 10)
        })
        data['Failure_Risk'] = np.random.choice([0, 1], size=10)

        X = data[['Temperature', 'Vibration', 'Uptime']]
        y = data['Failure_Risk']
        model = RandomForestClassifier().fit(X, y)
    
        data['Risk_Probability'] = (model.predict_proba(X)[:, 0] * 100).round(2)
        data['Risk_Probability'] = data['Risk_Probability'].astype(str) + '%'
        data['Risk_Probability'] = data['Risk_Probability'].replace('0.0%', '0%')
        data['Risk_Probability'] = data['Risk_Probability'].replace('100.0%', '100%')
        data['Risk_Probability'] = data['Risk_Probability'].replace('nan', '0%')
        data['Failure_Risk'] = data['Failure_Risk'].replace(0, 'No Risk')
        data['Failure_Risk'] = data['Failure_Risk'].replace(1, 'Risk')

        machine_data = data.to_dict()
        table_html = data.to_html(classes='table table-sm', index=False)
        
        return table_html, machine_data

    def production_slowdown(self):
    # 1) Simulate data
        data = pd.DataFrame({
            'Shift': np.random.choice([1, 2, 3], size=10),
            'Temp': np.random.normal(25, 5, 10),
            'Humidity': np.random.normal(50, 10, 10),
        })
        data['Actual_Rate'] = (
            100
            - (data['Temp'] * 0.5 + data['Humidity'] * 0.2 + data['Shift'] * 2)
            + np.random.normal(0, 5, 10)
        )

        # 2) Fit model & get raw impacts
        X = data[['Shift', 'Temp', 'Humidity']]
        y = data['Actual_Rate']
        model = LinearRegression().fit(X, y)
        data['Predicted_Rate'] = model.predict(X)

        coefs = model.coef_
        intercept = model.intercept_
        data['Shift_Impact']    = data['Shift']    * coefs[0]
        data['Temp_Impact']     = data['Temp']     * coefs[1]
        data['Humidity_Impact'] = data['Humidity'] * coefs[2]  
        data['Intercept'] = intercept

        # 3) Turn each impact into Low/Medium/High
        def categorize(v):
            if -1 <= v <= 1:
                return 'Low'
            elif -3 <= v < -1 or 1 < v <= 3:
                return 'Medium'
            else:
                return 'High'

        for feat in ('Shift_Impact', 'Temp_Impact', 'Humidity_Impact'):
            data[f'{feat}_Cat'] = data[feat].apply(categorize)
            del data[feat]
            data[feat.replace("_", " ")] = data.pop(f'{feat}_Cat')
        
        # 5) Summary counts
        summary = {
            feat: data[f'{feat}'].value_counts().to_dict()
            for feat in ('Shift Impact', 'Temp Impact', 'Humidity Impact')
        }

        # 6) Inline‐style mapping for categories
        def style_cat(cell_value):
            if cell_value == 'High':
                return 'background-color: lightcoral;'
            elif cell_value == 'Medium':
                return 'background-color: yellow;'
            else:  # Low
                return 'background-color: lightgreen;'

        # 7) Build Styler and output HTML
        styler = (
            data.style
                .applymap(style_cat, subset=[
                    'Shift Impact',
                    'Temp Impact',
                    'Humidity Impact'
                ])
                .set_table_attributes('class="table table-small"')
                .format(precision=2)
        )
        del data['Shift']
        table_html = styler.to_html()
        return table_html, summary

    def sensor_anomaly(self):
        # Simulate sensor readings with anomalies
        data = pd.DataFrame({
            'Sensor_1': np.random.normal(100, 5, 20),
            'Sensor_2': np.random.normal(200, 20, 20),
            'Sensor_3': np.append(np.random.normal(300, 15, 18), [500, 510])
        })
        sensor_data = data.copy()  # keep raw sensor readings

        model = IsolationForest(contamination=0.1).fit(sensor_data)
        data['Anomaly Score'] = model.decision_function(sensor_data)
        data['Anomaly Flag'] = pd.Series(model.predict(sensor_data)).map({1: 'Normal', -1: 'Anomaly'})

        table_html = data.to_html(classes='table table-sm', index=False)
        # Build summary
        sensor_summary = data.to_dict()
        return table_html, sensor_summary
    
    def impact_to_category(value):
        if -1 <= value <= 1:
            return 'Low'
        elif -3 <= value < -1 or 1 < value <= 3:
            return 'Medium'
        else:
            return 'High'
        