from flask import Flask, render_template, jsonify,
request, Response
import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import threading
import time
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

class NYISOWebCollector:
    """
    Web-based NYISO data collector with real-time
    updates
    """
    def __init__(self):
        self.base_urls = {
            'realtime_load': 'http://mis.nyiso.com/
public/csv/pal/{date}pal.csv',
            'realtime_lbmp': 'http://mis.nyiso.com/
public/csv/realtime/{date}realtime_zone.
csv',
            'fuel_mix': 'http://mis.nyiso.com/public/
csv/rtfuelmix/{date}rtfuelmix.csv'
        }
        self.db_connection = sqlite3.connect(
'nyiso_web.db', check_same_thread=False)
        self.setup_database()
        self.is_collecting = False
        self.collection_thread = None

    def setup_database(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_load (
                timestamp TEXT PRIMARY KEY,
                load REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_lbmp (
                timestamp TEXT PRIMARY KEY,
                zone TEXT,
                lbmp REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_mix (
                timestamp TEXT PRIMARY KEY,
                fuel_type TEXT,
                percentage REAL
            )
        ''')
        self.db_connection.commit()

    def collect_data(self):
        self.is_collecting = True
        while self.is_collecting:
            today = datetime.now().strftime('%Y%m%d')
            for data_type, url_template in self.base_urls.items():
                url = url_template.format(date=today)
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    content = response.text

                    if data_type == 'realtime_load':
                        df = pd.read_csv(io.StringIO(content))
                        for _, row in df.iterrows():
                            timestamp = datetime.strptime(row['Time Stamp'], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                            self.db_connection.execute(
                                "INSERT OR REPLACE INTO realtime_load (timestamp, load) VALUES (?, ?)",
                                (timestamp, row['Load'])
                            )
                    elif data_type == 'realtime_lbmp':
                        df = pd.read_csv(io.StringIO(content))
                        for _, row in df.iterrows():
                            timestamp = datetime.strptime(row['Time Stamp'], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                            self.db_connection.execute(
                                "INSERT OR REPLACE INTO realtime_lbmp (timestamp, zone, lbmp) VALUES (?, ?, ?)",
                                (timestamp, row['Name'], row['LBMP'])
                            )
                    elif data_type == 'fuel_mix':
                        df = pd.read_csv(io.StringIO(content))
                        for _, row in df.iterrows():
                            timestamp = datetime.strptime(row['Time Stamp'], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                            self.db_connection.execute(
                                "INSERT OR REPLACE INTO fuel_mix (timestamp, fuel_type, percentage) VALUES (?, ?, ?)",
                                (timestamp, row['Fuel Name'], row['Gen Pct'])
                            )
                    self.db_connection.commit()
                except requests.exceptions.RequestException as e:
                    print(f"Error collecting {data_type} data: {e}")
                except pd.errors.EmptyDataError:
                    print(f"No data for {data_type} on {today}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            time.sleep(300)  # Collect every 5 minutes

    def start_collection(self):
        if not self.is_collecting:
            self.collection_thread = threading.Thread(target=self.collect_data)
            self.collection_thread.daemon = True
            self.collection_thread.start()

    def stop_collection(self):
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join()

collector = NYISOWebCollector()
collector.start_collection()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/realtime_load')
def get_realtime_load():
    cursor = collector.db_connection.cursor()
    cursor.execute("SELECT timestamp, load FROM realtime_load ORDER BY timestamp DESC LIMIT 100")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/api/realtime_lbmp')
def get_realtime_lbmp():
    cursor = collector.db_connection.cursor()
    cursor.execute("SELECT timestamp, zone, lbmp FROM realtime_lbmp ORDER BY timestamp DESC LIMIT 100")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/api/fuel_mix')
def get_fuel_mix():
    cursor = collector.db_connection.cursor()
    cursor.execute("SELECT timestamp, fuel_type, percentage FROM fuel_mix ORDER BY timestamp DESC LIMIT 100")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/api/predict_load')
def predict_load():
    # This is a placeholder for a more complex prediction model
    # For demonstration, let's use a simple moving average or a basic ML model
    cursor = collector.db_connection.cursor()
    cursor.execute("SELECT load FROM realtime_load ORDER BY timestamp DESC LIMIT 24")
    past_loads = [row[0] for row in cursor.fetchall()]

    if len(past_loads) < 24:
        return jsonify({'error': 'Not enough data for prediction'}), 400

    # Simple RandomForestRegressor for demonstration
    # In a real scenario, you'd train this model with historical data
    X = np.arange(len(past_loads)).reshape(-1, 1)
    y = np.array(past_loads)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    future_X = np.arange(len(past_loads), len(past_loads) + 1).reshape(-1, 1)
    predicted_load = model.predict(future_X)[0]

    return jsonify({'predicted_load': predicted_load})

if __name__ == '__main__':
    import io
    collector.start_collection()
    app.run(debug=True)

