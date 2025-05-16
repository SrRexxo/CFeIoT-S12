import streamlit as st
from influxdb_client import InfluxDBClient
import pandas as pd
import plotly.express as px

# Configuración desde archivo local
from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET

# Consulta de datos (temperatura, humedad, niveles UV)
def query_sensor_data(fields, range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()

    field_filters = " or ".join([f'r._field == "{field}"' for field in fields])
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r._measurement == "airSensor")
      |> filter(fn: (r) => {field_filters})
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
    '''

    result = query_api.query_data_frame(query)
    if result.empty:
        return pd.DataFrame()

    result = result.rename(columns={"_time": "time"})
    result["time"] = pd.to_datetime(result["time"])
    return result

# Consulta de datos UV

def query_uv_data(range_minutes=60):
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()

    query = f'''
    from(bucket: "homeiot")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r._measurement == "uv_sensor")
      |> filter(fn: (r) => r._field == "uv_index" or r._field == "uv_raw")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"])
    '''

    result = query_api.query_data_frame(query)
    if result.empty:
        return pd.DataFrame()

    result = result.rename(columns={"_time": "time"})
    result["time"] = pd.to_datetime(result["time"])
    return result

# Configuración de la app
st.set_page_config(page_title="Monitoreo Ambiental", layout="wide")
st.title("Monitoreo Ambiental en Tiempo Real")

# Selector de tiempo
range_minutes = st.slider("Selecciona el rango de tiempo (en minutos):", 10, 180, 60)

# Consultar datos
fields = ["temperature", "humidity"]
data_df = query_sensor_data(fields, range_minutes)
uv_df = query_uv_data(range_minutes)

# Visualización
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌡️ Temperatura (°C)")
    if "temperature" in data_df.columns and not data_df.empty:
        st.plotly_chart(px.line(data_df, x="time", y="temperature", title="Temperatura"), use_container_width=True)
    else:
        st.info("Sin datos de temperatura en este rango.")

with col2:
    st.subheader("💧 Humedad (%)")
    if "humidity" in data_df.columns and not data_df.empty:
        st.plotly_chart(px.line(data_df, x="time", y="humidity", title="Humedad"), use_container_width=True)
    else:
        st.info("Sin datos de humedad en este rango.")

with col3:
    st.subheader("🌞 Índice UV")
    if "uv_index" in uv_df.columns and not uv_df.empty:
        st.plotly_chart(px.line(uv_df, x="time", y="uv_index", title="Índice UV"), use_container_width=True)
    else:
        st.info("Sin datos de índice UV en este rango.")
