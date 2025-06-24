# NYISO Dashboard

This project sets up a Flask-based dashboard to collect and display real-time data from NYISO (New York Independent System Operator). It includes data collection for real-time load, LBMP (Locational Based Marginal Price), and fuel mix, with a basic prediction model for load.

## Features

- Real-time data collection from NYISO.
- SQLite database for storing collected data.
- Flask API endpoints for accessing data.
- Basic load prediction using RandomForestRegressor.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd nyiso-dashboard
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Run the Flask application:**

    ```bash
    python app.py
    ```

    The application will start a web server and begin collecting data in the background.

## API Endpoints

- `/api/realtime_load`: Returns real-time load data.
- `/api/realtime_lbmp`: Returns real-time LBMP data.
- `/api/fuel_mix`: Returns real-time fuel mix data.
- `/api/predict_load`: Returns a predicted load value.

## Project Structure

- `app.py`: Main Flask application and data collection logic.
- `requirements.txt`: Python dependencies.
- `Procfile`: For Heroku deployment.
- `runtime.txt`: Specifies Python runtime for Heroku.
- `.gitignore`: Specifies files to ignore for Git.

## Deployment (Heroku Example)

1.  **Log in to Heroku CLI:**

    ```bash
    heroku login
    ```

2.  **Create a Heroku application:**

    ```bash
    heroku create your-app-name
    ```

3.  **Push to Heroku:**

    ```bash
    git add .
    git commit -m "Initial commit"
    git push heroku master
    ```

4.  **Open the application:**

    ```bash
    heroku open
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

