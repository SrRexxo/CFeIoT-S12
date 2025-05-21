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
st.subheader("📊 Datos Crudos")
if not data_df.empty:
    st.write("### Temperatura y Humedad", data_df)
else:
    st.info("No hay datos crudos disponibles para temperatura y humedad.")

if not uv_df.empty:
    st.write("### Índice UV", uv_df)
else:
    st.info("No hay datos crudos disponibles para índice UV.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🌡️ Temperatura (°C)")
    if "temperature" in data_df.columns and not data_df.empty:
        avg_temp = data_df["temperature"].mean()
        max_temp = data_df["temperature"].max()
        min_temp = data_df["temperature"].min()
        st.write(f"Promedio: {avg_temp:.2f} °C")
        st.write(f"Máximo: {max_temp:.2f} °C")
        st.write(f"Mínimo: {min_temp:.2f} °C")
        st.plotly_chart(px.line(data_df, x="time", y="temperature", title="Temperatura"), use_container_width=True)
    else:
        st.info("Sin datos de temperatura en este rango.")

with col2:
    st.subheader("💧 Humedad (%)")
    if "humidity" in data_df.columns and not data_df.empty:
        avg_hum = data_df["humidity"].mean()
        max_hum = data_df["humidity"].max()
        min_hum = data_df["humidity"].min()
        st.write(f"Promedio: {avg_hum:.2f} %")
        st.write(f"Máximo: {max_hum:.2f} %")
        st.write(f"Mínimo: {min_hum:.2f} %")
        st.plotly_chart(px.line(data_df, x="time", y="humidity", title="Humedad"), use_container_width=True)
    else:
        st.info("Sin datos de humedad en este rango.")

with col3:
    st.subheader("🌞 Índice UV")
    st.write("Datos UV crudos:")
    st.write(uv_df.head())  
    st.write("Columnas:", uv_df.columns)
    if "uv_raw" in uv_df.columns and not uv_df.empty:
        uv_df["uv_raw"] = pd.to_numeric(uv_df["uv_raw"], errors="coerce")
        uv_df = uv_df.dropna(subset=["uv_raw"])
        
        if not uv_df.empty:
            avg_uv = uv_df["uv_raw"].mean()
            max_uv = uv_df["uv_raw"].max()
            min_uv = uv_df["uv_raw"].min()
            st.write(f"Promedio: {avg_uv:.2f}")
            st.write(f"Máximo: {max_uv:.2f}")
            st.write(f"Mínimo: {min_uv:.2f}")
            #st.plotly_chart(px.line(uv_df, x="time", y="uv_raw", title="Índice UV"), use_container_width=True)
            if len(uv_df) > 1:

                st.plotly_chart(

                px.line(uv_df, x="time", y="uv_raw", title="Índice UV"),

                use_container_width=True

            )
 
        else:
            st.info("No hay datos válidos de índice UV en este rango.")
    else:
        st.info("Sin datos de índice UV en este rango.")

# Recomendaciones automatizadas
st.subheader("🌱 Recomendaciones para el cuidado de microcultivos")
if "humidity" in data_df.columns and not data_df.empty:
    last_humidity = data_df["humidity"].iloc[-1]
    if last_humidity < 30:
        st.warning("La humedad está por debajo del umbral recomendado. Se sugiere regar los cultivos.")
    elif last_humidity > 60:
        st.success("La humedad está en un rango óptimo para los cultivos.")
    else:
        st.info("La humedad es moderada. Monitorea para mantenerla estable.")

if "uv_index" in uv_df.columns and not uv_df.empty:
    last_uv = uv_df["uv_index"].iloc[-1]
    if last_uv > 8:
        st.error("La radiación UV es alta. Se recomienda proteger los cultivos con sombra o cobertores.")
    elif last_uv > 5:
        st.warning("La radiación UV es moderada. Considera medidas preventivas para evitar daños.")
    else:
        st.success("La radiación UV está en niveles seguros.")
