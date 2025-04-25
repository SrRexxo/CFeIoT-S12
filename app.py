import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import streamlit.components.v1 as components
import plotly.express as px
import numpy as np

# Configuración desde archivo local
from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET

# Función para consultar múltiples campos de un mismo measurement
def query_accelerometer_data(range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()

    query = f'''
    import "math"
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "accelerometer" and r["_field"] == "ax" or r["_field"] == "ay" or r["_field"] == "az")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
    '''

    result = query_api.query_data_frame(query)
    if result.empty:
        return pd.DataFrame()

    # Renombrar y calcular magnitud
    result = result.rename(columns={"_time": "time"})
    result["accel_magnitude"] = np.sqrt(result["ax"]**2 + result["ay"]**2 + result["az"]**2)
    result["time"] = pd.to_datetime(result["time"])
    return result[["time", "accel_magnitude"]]

# Consulta giroscopio
def query_gyroscope_data(range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()

    query = f'''
    import "math"
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "accelerometer" and (r["_field"] == "gx" or r["_field"] == "gy" or r["_field"] == "gz"))
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
    '''

    result = query_api.query_data_frame(query)
    if result.empty:
        return pd.DataFrame()

    result = result.rename(columns={"_time": "time"})
    result["gyro_magnitude"] = np.sqrt(result["gx"]**2 + result["gy"]**2 + result["gz"]**2)
    result["time"] = pd.to_datetime(result["time"])
    return result[["time", "gx", "gy", "gz", "gyro_magnitude"]]

# Consulta simple de un solo campo
def query_data(measurement, field, range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()

    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["_field"] == "{field}")
      |> sort(columns: ["_time"])
    '''

    result = query_api.query(query)
    data = []

    for table in result:
        for record in table.records:
            data.append({"time": record.get_time(), field: record.get_value()})

    df = pd.DataFrame(data)
    if not df.empty:
        df["time"] = pd.to_datetime(df["time"])
    return df

# Configuración de la app
st.set_page_config(page_title="🌿 Koru – Jardín Inteligente", layout="wide")
st.title("🌿 Koru – Jardín Inteligente para la Calma")
st.markdown("Monitorea en tiempo real los datos de tu planta: temperatura, humedad y movimiento.")

# Selector de tiempo
range_minutes = st.slider("Selecciona el rango de tiempo (en minutos):", 10, 180, 60)

# Consultas
temp_df = query_data("airSensor", "temperature", range_minutes)
hum_df = query_data("airSensor", "humidity", range_minutes)
mov_df = query_accelerometer_data(range_minutes)
gyr_df = query_gyroscope_data(range_minutes)

# Visualización
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡️ Temperatura (°C)")
    if not temp_df.empty:
        st.plotly_chart(px.line(temp_df, x="time", y="temperature", title="Temperatura"), use_container_width=True)
    else:
        st.info("Sin datos de temperatura en este rango.")

with col2:
    st.subheader("💧 Humedad (%)")
    if not hum_df.empty:
        st.plotly_chart(px.line(hum_df, x="time", y="humidity", title="Humedad"), use_container_width=True)
    else:
        st.info("Sin datos de humedad en este rango.")

st.subheader("📈 Movimiento (magnitud del acelerómetro)")
if not mov_df.empty:
    st.plotly_chart(px.line(mov_df, x="time", y="accel_magnitude", title="Movimiento"), use_container_width=True)
else:
    st.info("Sin datos de movimiento en este rango.")


st.subheader("🧭 Giroscopio (gx, gy, gz y magnitud)")
if not gyr_df.empty:
    fig = px.line(gyr_df, x="time", y=["gx", "gy", "gz", "gyro_magnitude"], title="Datos del Giroscopio")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sin datos del giroscopio en este rango.")

def get_plant_state(hum_df):
    if hum_df.empty:
        return "neutra", "🌥️", "Sin datos de humedad."

    last_value = hum_df["humidity"].iloc[-1]
    last_value= 40

    if last_value > 60:
        return "feliz", "🌞", f"Humedad alta ({last_value:.1f}%) — la planta está feliz."
    elif last_value < 30:
        return "triste", "🌧️", f"Humedad baja ({last_value:.1f}%) — la planta está triste."
    else:
        return "neutra", "🌥️", f"Humedad moderada ({last_value:.1f}%) — la planta está normal."

# Obtener el estado actual de la planta
estado, emoji, mensaje = get_plant_state(hum_df)

# Mostrar mensaje de estado
st.subheader(f"Estado de la Planta: {emoji}")
st.markdown(mensaje)

# HTML animado para cada estado
html_animaciones = {
    "feliz": """
        <div style="text-align:center;">
            <div style="width:160px;height:160px;margin:auto;border-radius:50%;background: radial-gradient(circle at 30% 30%, #f9d423, #ff4e50); animation: pulse 2s infinite;">
                <div style="font-size:80px;line-height:160px;">🌼</div>
            </div>
            <p style="font-size:20px;">¡Estoy feliz y brillante!</p>
        </div>
        <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        </style>
    """,
    "triste": """
        <div style="text-align:center;">
            <div style="width:160px;height:160px;margin:auto;border-radius:50%;background: linear-gradient(to bottom, #89f7fe, #66a6ff); animation: rain 1.2s infinite;">
                <div style="font-size:80px;line-height:160px;">💧</div>
            </div>
            <p style="font-size:20px;">Me siento seca... 😢</p>
        </div>
        <style>
        @keyframes rain {
            0% { transform: translateY(0px); }
            50% { transform: translateY(6px); }
            100% { transform: translateY(0px); }
        }
        </style>
    """,
    "neutra": """
        <div style="text-align:center;">
            <div style="width:160px;height:160px;margin:auto;border-radius:50%;background: radial-gradient(circle at center, #c9d6ff, #e2e2e2); animation: float 3s ease-in-out infinite;">
                <div style="font-size:80px;line-height:160px;">🍃</div>
            </div>
            <p style="font-size:20px;">Estoy tranquila 🌥️</p>
        </div>
        <style>
        @keyframes float {
            0% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0); }
        }
        </style>
    """
}

# Renderizar animación basada en estado
components.html(html_animaciones[estado], height=300)


