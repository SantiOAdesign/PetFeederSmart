import streamlit as st

import estilo
import perfil

NOMBRE_MASCOTA = perfil.cargar()["nombre"]

estilo.encabezado("🐾", "PetFeeder/Smart",
                  f"Alimenta a {NOMBRE_MASCOTA} desde cualquier lugar, con un botón, tu voz o un mensaje.")

st.write(
    f"Controla el dispensador de comida de **{NOMBRE_MASCOTA}** en tiempo real "
    "y revisa cómo y cuándo está comiendo. El dispensador es un ESP32 simulado en "
    "Wokwi que se comunica con esta app por MQTT."
)

c1, c2, c3 = st.columns(3)
with c1, st.container(border=True):
    st.markdown("### 🏠 Modo Doméstico")
    st.write("Sirve comida con un botón, por voz o escribiendo una orden. "
             "Ajusta la porción y mira el nivel del contenedor.")
    st.page_link("vistas/domestico.py", label="Ir al Modo Doméstico", icon="➡️")
with c2, st.container(border=True):
    st.markdown("### 📊 Analítica y Salud")
    st.write("Historial de comidas, horarios automáticos, alertas y "
             "hábitos frente a la ración diaria recomendada.")
    st.page_link("vistas/analitica.py", label="Ir a Analítica", icon="➡️")
with c3, st.container(border=True):
    st.markdown("### 🐶 Mi mascota")
    st.write(f"¿Tu mascota no se llama {NOMBRE_MASCOTA}? Cambia su nombre, "
             "la porción por defecto y las notificaciones.")
    st.page_link("vistas/mascota.py", label="Editar perfil", icon="➡️")

estilo.seccion("Prueba decir o escribir")
estilo.ejemplos([f"Oye app, dale de comer a {NOMBRE_MASCOTA}", "Sirve 80 gramos", "Rellena el contenedor"])
