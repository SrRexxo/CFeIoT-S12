# 🌿 Koru - Jardín Inteligente para la Calma

Koru es una experiencia de diseño interactivo que fusiona el Internet de las Cosas (IoT), la naturaleza y el bienestar. A través de una maceta inteligente equipada con sensores de temperatura, humedad y movimiento, y una aplicación web construida con Streamlit, el sistema permite visualizar el estado de una planta en tiempo real, fomentando la conexión con el entorno natural.

## ✨ Concepto

Inspirado en el símbolo maorí del helecho en espiral (“koru”), este proyecto busca promover la atención plena y el cuidado personal mediante el monitoreo ambiental y físico de una planta, convertida en un canal de comunicación entre la naturaleza y el usuario.

## 🛠 Tecnologías utilizadas

- **ESP32** – Microcontrolador con WiFi
- **DHT22** – Sensor de temperatura y humedad
- **MPU6050** – Sensor de aceleración y giroscopio
- **InfluxDB** – Base de datos de series temporales
- **Python** – Lógica y análisis de datos
- **Streamlit** – Visualización web interactiva
- **GitHub** – Repositorio y control de versiones

## 🔌 Arquitectura del sistema

[ESP32 + DHT22 + MPU6050] | WiFi | [InfluxDB] | [Python App] | [Streamlit WebApp]

## 📊 Funcionalidades de la aplicación

- Dashboard en tiempo real de temperatura, humedad y movimiento.
- Alertas visuales y recomendaciones (riego, movimiento brusco).
- Visualizaciones de datos históricos (gráficas interactivas).
- Interfaz amigable, estética meditativa y minimalista.

## 🚀 Cómo ejecutar el proyecto

1. **Clona este repositorio:**
```
git clone https://github.com/tuusuario/koru.git
cd koru
```

2.  **Instala las dependencias:**
   ```
   pip install -r requirements.txt
   ```

3.  **Configura las variables de conexión a InfluxDB en el archivo**
   ```
   config.py
   ```

4.  **Ejecuta la aplicación con Streamlit:**
   ```   
   streamlit run app.py
   ```

5.  **Accede a la interfaz en tu navegador:**

   http://localhost:8501


## 📁 Estructura del repositorio
koru/
├── app.py               # Aplicación principal de Streamlit
├── config.py            # Configuración de InfluxDB y otros parámetros
├── sensors/             # Scripts para leer y enviar datos desde el ESP32
├── utils/               # Funciones auxiliares para procesar datos
├── assets/              # Imágenes, estilos y recursos visuales
├── requirements.txt     # Lista de dependencias
└── README.md

## 🌱 Créditos

Proyecto desarrollado para la clase de Computación Física e Internet de las Cosas, carrera de Diseño Interactivo.

Desarrollado por: Miguel Angel Carrillo
Licencia: MIT
