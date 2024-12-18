from flask import Flask, render_template, request, redirect, url_for
import pickle
import pandas as pd
import numpy as np

# Load the trained model and scaler
with open('aqi_rf_model_final.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

app = Flask(__name__)

# Function to categorize AQI values
def categorize_aqi(aqi):
    if aqi <= 50:
        return "Good", "Air quality is considered satisfactory."
    elif aqi <= 100:
        return "Moderate", "Air quality is acceptable."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "People with respiratory conditions should reduce outdoor activities."
    elif aqi <= 200:
        return "Unhealthy", "Everyone may start to feel health effects."
    elif aqi <= 300:
        return "Very Unhealthy", "Health alert: everyone may experience serious health effects."
    else:
        return "Hazardous", "Emergency conditions: the entire population is likely to be affected."

# Function to suggest solutions based on feature contribution
def suggest_solutions(input_values):
    # Determine which feature has the highest value
    pollutants = ['PM2.5', 'NO', 'NO2', 'NOx', 'CO', 'SO2', 'O3']
    max_pollutant = pollutants[np.argmax(input_values)]
    
    # Provide suggestions based on the highest contributor
    if max_pollutant == 'PM2.5':
        return "Reduce PM2.5 by limiting vehicle emissions and using cleaner fuels."
    elif max_pollutant == 'NO':
        return "Reduce NO levels by using public transport or carpooling."
    elif max_pollutant == 'NO2':
        return "Improve NO2 levels by reducing industrial emissions."
    elif max_pollutant == 'NOx':
        return "Lower NOx by limiting fossil fuel combustion and vehicle emissions."
    elif max_pollutant == 'CO':
        return "Reduce CO by using clean energy sources and improving ventilation."
    elif max_pollutant == 'SO2':
        return "Reduce SO2 by minimizing coal use and promoting clean energy."
    elif max_pollutant == 'O3':
        return "Reduce O3 by avoiding the use of gas-powered engines during hot weather."
    else:
        return "Maintain clean air practices."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values from the form
        pm25 = float(request.form['PM2.5'])
        no = float(request.form['NO'])
        no2 = float(request.form['NO2'])
        nox = float(request.form['NOx'])
        co = float(request.form['CO'])
        so2 = float(request.form['SO2'])
        o3 = float(request.form['O3'])

        # Create DataFrame for input data
        input_data = pd.DataFrame([[pm25, no, no2, nox, co, so2, o3]], 
                                   columns=['PM2.5', 'NO', 'NO2', 'NOx', 'CO', 'SO2', 'O3'])

        # Scale input data
        scaled_data = scaler.transform(input_data)

        # Make prediction
        prediction = model.predict(scaled_data)

        # Format the prediction to 2 decimal places
        formatted_prediction = round(prediction[0], 2)

        # Categorize AQI
        category, health_advice = categorize_aqi(formatted_prediction)

        # Suggest solutions based on highest contributing pollutant
        solutions = suggest_solutions([pm25, no, no2, nox, co, so2, o3])

        # Pass inputs, prediction, category, and suggestions to the template
        return render_template('index.html', 
                               prediction=formatted_prediction, 
                               category=category, 
                               health_advice=health_advice,
                               solutions=solutions,
                               pm25=pm25, no=no, no2=no2, nox=nox, co=co, so2=so2, o3=o3)

    except Exception as e:
        return str(e)

@app.route('/refresh')
def refresh():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

