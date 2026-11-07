"""
PetFeeder/Smart — App Streamlit
Ejecutar desde la raíz del repositorio:
    streamlit run app/app.py
"""

from html import escape

import streamlit as st

import estilo
import perfil
from feedback import reproducir
from mqtt_client import get_mqtt

st.set_page_config(page_title="PetFeeder/Smart", page_icon="🐾", layout="wide")

paginas = st.navigation([
    st.Page("vistas/inicio.py", title="Inicio", icon="🐾", default=True),
    st.Page("vistas/domestico.py", title="Modo Doméstico", icon="🏠"),
    st.Page("vistas/analitica.py", title="Analítica y Salud", icon="📊"),
    st.Page("vistas/mascota.py", title="Mi mascota", icon="🐶"),
])

estilo.aplicar()
mq = get_mqtt()

MENSAJES_ERROR = {
    "contenedor_vacio": "El contenedor está vacío. Rellénalo para poder servir.",
    "ya_sirviendo": "El dispensador ya está sirviendo, espera un momento.",
    "accion_desconocida": "El dispensador no reconoció la orden.",
}


def notificar(ev: dict, nombre: str, p: dict, uid: int):
    """Toast + sonido + vibración para cada evento nuevo del ESP32."""
    tipo = ev["evento"]
    if tipo == "inicio" and ev.get("origen") == "horario":
        st.toast(f"Comida programada: sirviendo {ev['gramos']} g a {nombre}…", icon="⏰")
    elif tipo == "inicio":
        st.toast(f"Sirviendo {ev['gramos']} g a {nombre}…", icon="🍖")
    elif tipo == "servido":
        st.toast(f"{nombre} recibió {ev['gramos']} g", icon="✅")
    elif tipo == "alerta":
        st.toast("Contenedor bajo: rellénalo pronto", icon="⚠️")
    elif tipo == "rellenado":
        st.toast("Contenedor rellenado", icon="🔄")
    elif tipo == "horarios":
        st.toast(f"El dispensador confirmó: {ev['detalle']}", icon="⏰")
    elif tipo == "error":
        st.toast(MENSAJES_ERROR.get(ev["detalle"], "Error en el dispensador"), icon="❌")
    reproducir(tipo, sonido=p["sonido"], vibracion=p["vibracion"], uid=uid)


@st.fragment(run_every=1)
def barra_lateral():
    s = mq.snapshot()
    p = perfil.cargar()

    ultimo = f"Último dato: {s['ultima_actualizacion']:%H:%M:%S}" if s["ultima_actualizacion"] else "Esperando datos…"
    st.html(
        f'<div class="pf-mascota"><div class="pf-avatar">🐶</div>'
        f'<div><b>{escape(p["nombre"])}</b><span>{ultimo}</span></div></div>'
        + estilo.chip_estado("Broker MQTT", s["broker_conectado"])
        + estilo.chip_estado("Dispensador", s["esp32_online"])
    )

    # Eventos nuevos → notificación en cualquier página de la app
    if "eventos_vistos" not in st.session_state:
        st.session_state.eventos_vistos = s["contador_eventos"]
    nuevos = s["contador_eventos"] - st.session_state.eventos_vistos
    if nuevos > 0:
        recientes = s["eventos"][-nuevos:]
        for i, ev in enumerate(recientes):
            notificar(ev, p["nombre"], p, uid=st.session_state.eventos_vistos + i + 1)
        st.session_state.eventos_vistos = s["contador_eventos"]


with st.sidebar:
    barra_lateral()

paginas.run()
