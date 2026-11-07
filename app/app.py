"""
PetFeeder/Smart — App Streamlit
Ejecutar desde la raíz del repositorio:
    streamlit run app/app.py
"""

import streamlit as st

from mqtt_client import get_mqtt

st.set_page_config(page_title="PetFeeder/Smart", page_icon="🐾", layout="wide")

paginas = st.navigation([
    st.Page("vistas/inicio.py", title="Inicio", icon="🐾", default=True),
    st.Page("vistas/domestico.py", title="Modo Doméstico", icon="🏠"),
    st.Page("vistas/analitica.py", title="Analítica y Salud", icon="📊"),
])

mq = get_mqtt()


@st.fragment(run_every=3)
def estado_conexion():
    s = mq.snapshot()
    st.markdown("**Conexión**")
    st.write(("🟢" if s["broker_conectado"] else "🔴") + " Broker MQTT")
    st.write(("🟢" if s["esp32_online"] else "🔴") + " Dispensador (ESP32)")
    if s["ultima_actualizacion"]:
        st.caption(f"Último dato: {s['ultima_actualizacion']:%H:%M:%S}")


with st.sidebar:
    estado_conexion()

paginas.run()
