"""Ambiente 1 — Modo Doméstico: control en tiempo real del dispensador."""

from pathlib import Path

import streamlit as st
from streamlit_mic_recorder import speech_to_text

from comandos import interpretar
from config import GRAMOS_DEFECTO, NOMBRE_MASCOTA
from mqtt_client import get_mqtt

mq = get_mqtt()
SONIDO_CROQUETAS = Path(__file__).parent.parent / "assets" / "croquetas.mp3"

MENSAJES_ERROR = {
    "contenedor_vacio": "El contenedor está vacío. Rellénalo para poder servir.",
    "ya_sirviendo": "El dispensador ya está sirviendo, espera un momento.",
    "accion_desconocida": "El dispensador no reconoció la orden.",
}

st.title("🏠 Modo Doméstico")
st.caption(f"Controla la comida de {NOMBRE_MASCOTA} en tiempo real.")


# ── Estado en vivo + feedback de eventos ─────────────────────
@st.fragment(run_every=1)
def panel_estado():
    s = mq.snapshot()
    e = s["estado"]

    if not s["esp32_online"]:
        st.warning("El dispensador no está conectado. Inicia la simulación en Wokwi.", icon="🔌")

    c1, c2, c3 = st.columns(3)
    with c1, st.container(border=True):
        st.markdown("**Contenedor**")
        if "nivel_pct" in e:
            st.progress(max(0, min(100, e["nivel_pct"])) / 100,
                        text=f"{e['nivel_pct']} %  ·  {e['nivel_g']} g")
        else:
            st.write("Sin datos aún")
    with c2, st.container(border=True):
        st.markdown("**Compuerta**")
        abierta = e.get("compuerta") == "abierta"
        st.markdown("### 🟢 Sirviendo..." if abierta else "### ⚪ Cerrada")
    with c3, st.container(border=True):
        st.markdown("**Última porción**")
        st.markdown(f"### {e.get('ultima_porcion_g', 0)} g")
        st.caption(f"Origen: {e.get('ultimo_origen', '—')} · Porciones hoy (sesión): {e.get('porciones', 0)}")

    if e.get("alerta"):
        st.error("Nivel de comida bajo: rellena el contenedor pronto.", icon="⚠️")

    # Eventos nuevos desde la última actualización → feedback visual y sonoro
    if "eventos_vistos" not in st.session_state:
        st.session_state.eventos_vistos = s["contador_eventos"]
    nuevos = s["contador_eventos"] - st.session_state.eventos_vistos
    if nuevos > 0:
        for ev in s["eventos"][-nuevos:]:
            if ev["evento"] == "inicio":
                st.toast(f"Sirviendo {ev['gramos']} g a {NOMBRE_MASCOTA}…", icon="🍖")
                if SONIDO_CROQUETAS.exists():
                    st.audio(str(SONIDO_CROQUETAS), autoplay=True)
            elif ev["evento"] == "servido":
                st.toast(f"{NOMBRE_MASCOTA} recibió {ev['gramos']} g", icon="✅")
            elif ev["evento"] == "alerta":
                st.toast("Contenedor bajo", icon="⚠️")
            elif ev["evento"] == "rellenado":
                st.toast("Contenedor rellenado", icon="🔄")
            elif ev["evento"] == "error":
                st.toast(MENSAJES_ERROR.get(ev["detalle"], "Error en el dispensador"), icon="❌")
        st.session_state.eventos_vistos = s["contador_eventos"]


panel_estado()


# ── Ejecutar un comando venga de donde venga ─────────────────
def ejecutar(comando: dict | None, origen: str):
    if comando is None:
        st.warning(f"No entendí la orden. Prueba con “dale de comer a {NOMBRE_MASCOTA}”, "
                   "“sirve 80 gramos” o “rellena el contenedor”.")
        return
    if comando["accion"] == "servir":
        ok = mq.servir(comando["gramos"], origen)
        texto = f"Orden enviada: servir {comando['gramos']} g"
    elif comando["accion"] == "rellenar":
        ok = mq.rellenar()
        texto = "Orden enviada: rellenar contenedor"
    else:
        ok = mq.pedir_estado()
        texto = "Consultando el estado del dispensador"

    if ok:
        st.success(texto)
    else:
        st.error("No hay conexión con el broker MQTT. Intenta de nuevo en unos segundos.")


# ── Modalidades de interacción ───────────────────────────────
st.subheader("Dar de comer")
tab_botones, tab_voz, tab_texto = st.tabs(["👆 Botones", "🎙️ Voz", "⌨️ Texto"])

with tab_botones:
    gramos = st.slider("Porción (gramos)", 5, 200, GRAMOS_DEFECTO, step=5)
    b1, b2 = st.columns(2)
    if b1.button(f"🍖 Servir {gramos} g", type="primary", use_container_width=True):
        ejecutar({"accion": "servir", "gramos": gramos}, "boton")
    if b2.button("🔄 Rellenar contenedor", use_container_width=True):
        ejecutar({"accion": "rellenar"}, "boton")

with tab_voz:
    st.write("Pulsa el botón, di la orden y pulsa detener.")
    texto_voz = speech_to_text(
        language="es",
        start_prompt="🎙️ Hablar",
        stop_prompt="⏹️ Detener",
        just_once=True,
        key="voz",
    )
    if texto_voz:
        st.info(f"Escuché: “{texto_voz}”")
        ejecutar(interpretar(texto_voz), "voz")

with tab_texto:
    with st.form("form_texto", clear_on_submit=True):
        texto = st.text_input("Escribe una orden", placeholder=f"Dale de comer a {NOMBRE_MASCOTA}")
        enviado = st.form_submit_button("Enviar")
    if enviado and texto:
        ejecutar(interpretar(texto), "texto")
