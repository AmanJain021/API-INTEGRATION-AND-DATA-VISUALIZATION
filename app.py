
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Streamlit page config
st.set_page_config(page_title="Aman's Weather Dashboard", layout="centered")
st.title("🌤️ Aman's Weather - Forecast Dashboard")

# OpenWeatherMap API Setup
API_KEY = "abe1d134ae5dc630ba17ccc596910783"
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Input city
city = st.text_input("Enter City Name", "Jaipur")

# Function to fetch and process weather data
def fetch_weather(city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    res = requests.get(BASE_URL, params=params)
    if res.status_code == 200:
        data = res.json()
        records = []
        for entry in data['list']:
            records.append({
                'datetime': datetime.fromtimestamp(entry['dt']),
                'temperature': entry['main']['temp'],
                'temp_min': entry['main']['temp_min'],
                'temp_max': entry['main']['temp_max'],
                'humidity': entry['main']['humidity'],
                'wind_speed': entry['wind']['speed'],
                'rain': entry.get('rain', {}).get('3h', 0),  # Handle missing rain
                'weather': entry['weather'][0]['main']
            })
        return pd.DataFrame(records)
    else:
        st.error("❌ Failed to fetch data. Check the city name or API key.")
        return None

# Button to fetch forecast
if st.button("Fetch Forecast"):
    df = fetch_weather(city)
    if df is not None and not df.empty:
        st.session_state['weather_df'] = df
    else:
        st.warning("No weather data available.")

# Only show plot section if data is already fetched
if 'weather_df' in st.session_state:
    df = st.session_state['weather_df']

    st.subheader(f"Forecast for {city}")
    option = st.radio("Choose data to visualize:", ("Temperature", "Humidity", "Wind Speed", "Rain", "Min/Max Temperature"))

    fig, ax = plt.subplots(figsize=(10, 4))

    if option == "Temperature":
        sns.lineplot(data=df, x="datetime", y="temperature", ax=ax, marker='o', color='red')
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("Temperature Forecast")
    elif option == "Humidity":
        sns.lineplot(data=df, x="datetime", y="humidity", ax=ax, marker='o', color='blue')
        ax.set_ylabel("Humidity (%)")
        ax.set_title("Humidity Forecast")
    elif option == "Wind Speed":
        sns.lineplot(data=df, x="datetime", y="wind_speed", ax=ax, marker='o', color='green')
        ax.set_ylabel("Wind Speed (m/s)")
        ax.set_title("Wind Speed Forecast")
    elif option == "Rain":
        sns.barplot(data=df, x="datetime", y="rain", ax=ax, color='skyblue')
        ax.set_ylabel("Rainfall (mm)")
        ax.set_title("Rain Forecast (Next 3h Interval)")
    elif option == "Min/Max Temperature":
        sns.lineplot(data=df, x="datetime", y="temp_min", ax=ax, marker='o', label='Min Temp', color='purple')
        sns.lineplot(data=df, x="datetime", y="temp_max", ax=ax, marker='o', label='Max Temp', color='orange')
        ax.set_ylabel("Temperature (°C)")
        ax.set_title("Min/Max Temperature Forecast")
        ax.legend()

    ax.set_xlabel("Date & Time")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

    # Weather condition pie chart
    st.subheader("Weather Conditions Distribution")
    condition_counts = df['weather'].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(condition_counts, labels=condition_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)
else:
    st.info("🔎 Enter a city name and click 'Fetch Forecast' to begin.")
