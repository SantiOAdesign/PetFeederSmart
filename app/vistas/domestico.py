"""Ambiente 1 — Modo Doméstico: control en tiempo real del dispensador."""

import streamlit as st
from streamlit_mic_recorder import speech_to_text

import estilo
import perfil
from comandos import interpretar
from mqtt_client import get_mqtt

mq = get_mqtt()
datos = perfil.cargar()
NOMBRE_MASCOTA = datos["nombre"]
GRAMOS_DEFECTO = int(datos["gramos_defecto"])

estilo.encabezado("🏠", "Modo Doméstico", f"Controla la comida de {NOMBRE_MASCOTA} en tiempo real.")


# ── Estado en vivo + feedback de eventos ─────────────────────
@st.fragment(run_every=1)
def panel_estado():
    s = mq.snapshot()
    e = s["estado"]

    if not s["esp32_online"]:
        st.warning("El dispensador no está conectado. Inicia la simulación en Wokwi.", icon="🔌")

    if "nivel_pct" in e:
        pct = max(0, min(100, e["nivel_pct"]))
        t_cont = estilo.tarjeta("🥣", "Contenedor", f"{pct} %", f"{e['nivel_g']} g disponibles",
                                extra_html=estilo.barra(pct))
    else:
        t_cont = estilo.tarjeta("🥣", "Contenedor", "—", "Sin datos aún")

    abierta = e.get("compuerta") == "abierta"
    estado_comp = (estilo.punto(estilo.VERDE, pulso=True) + "Sirviendo…") if abierta         else (estilo.punto("#C9B8A8") + "Cerrada")
    proximo = (f"⏰ Próxima comida: <b>{e['proximo']}</b> ({e.get('proximo_g', '?')} g)"
               if e.get("proximo") else "⏰ Sin horarios programados")
    t_comp = estilo.tarjeta("🚪", "Compuerta", f'<span style="font-size:1.4rem">{estado_comp}</span>', proximo)

    t_ult = estilo.tarjeta("🍖", "Última porción", f"{e.get('ultima_porcion_g', 0)} g",
                           f"Origen: {e.get('ultimo_origen', '—')} · {e.get('porciones', 0)} porciones desde que encendió")
    estilo.grilla(t_cont, t_comp, t_ult)

    if e.get("alerta"):
        st.error("Nivel de comida bajo: rellena el contenedor pronto.", icon="⚠️")


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
estilo.seccion("Dar de comer")
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
        ejecutar(interpretar(texto_voz, GRAMOS_DEFECTO), "voz")

with tab_texto:
    with st.form("form_texto", clear_on_submit=True):
        texto = st.text_input("Escribe una orden", placeholder=f"Dale de comer a {NOMBRE_MASCOTA}")
        enviado = st.form_submit_button("Enviar")
    if enviado and texto:
        ejecutar(interpretar(texto, GRAMOS_DEFECTO), "texto")
