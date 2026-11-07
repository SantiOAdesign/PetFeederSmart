import streamlit as st

from config import NOMBRE_MASCOTA

st.title("🐾 PetFeeder/Smart")
st.subheader("Alimenta a tu mascota desde cualquier lugar")

st.write(
    f"Controla el dispensador de comida de **{NOMBRE_MASCOTA}** en tiempo real "
    "y revisa cómo y cuándo está comiendo. El dispensador es un ESP32 simulado en "
    "Wokwi que se comunica con esta app por MQTT."
)

c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("### 🏠 Modo Doméstico")
        st.write("Sirve comida con un botón, por voz o escribiendo una orden. "
                 "Ajusta la porción en gramos y mira el nivel del contenedor.")
        st.page_link("vistas/domestico.py", label="Ir al Modo Doméstico", icon="➡️")
with c2:
    with st.container(border=True):
        st.markdown("### 📊 Analítica y Salud")
        st.write("Historial de comidas, horarios, alertas del contenedor y "
                 "hábitos de alimentación frente a la ración diaria recomendada.")
        st.page_link("vistas/analitica.py", label="Ir a Analítica", icon="➡️")

st.divider()
st.markdown("**Prueba decir o escribir:**")
st.markdown(f"- *“Oye app, dale de comer a {NOMBRE_MASCOTA}”*\n"
            "- *“Sirve 80 gramos”*\n"
            "- *“Rellena el contenedor”*")
