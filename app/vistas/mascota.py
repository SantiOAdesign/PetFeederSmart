"""Perfil de la mascota y preferencias de notificación."""

import streamlit as st

import estilo
import perfil
from feedback import reproducir

datos = perfil.cargar()

estilo.encabezado("🐶", "Mi mascota", "Estos datos se usan en toda la app y en la analítica de salud.")

with st.form("perfil"):
    nombre = st.text_input("Nombre de tu mascota", value=datos["nombre"], max_chars=30)
    c1, c2 = st.columns(2)
    gramos = c1.number_input("Porción por defecto (g)", 5, 200, int(datos["gramos_defecto"]), step=5,
                             help="Lo que se sirve cuando dices “dale de comer” sin decir cuánto.")
    meta = c2.number_input("Ración diaria recomendada (g)", 50, 2000, int(datos["meta_diaria_g"]), step=10,
                           help="Consulta con tu veterinario la cantidad ideal según peso y edad.")
    st.markdown("**Notificaciones**")
    sonido = st.toggle("🔊 Sonido de croquetas al servir y pitido en alertas", value=datos["sonido"])
    vibracion = st.toggle("📳 Vibración en el celular (Android)", value=datos["vibracion"])
    guardado = st.form_submit_button("Guardar", type="primary")

if guardado:
    perfil.guardar({"nombre": nombre, "gramos_defecto": gramos, "meta_diaria_g": meta,
                    "sonido": sonido, "vibracion": vibracion})
    st.success(f"Perfil guardado. ¡Hola, {nombre.strip() or datos['nombre']}! 🐾")

estilo.seccion("Probar notificaciones")
st.caption("Úsalo también al abrir la app en el celular: el navegador solo permite "
           "sonido y vibración después de que tocas algo en la página.")
if st.button("▶️ Probar sonido y vibración"):
    actual = perfil.cargar()
    reproducir("prueba", sonido=actual["sonido"], vibracion=actual["vibracion"],
               uid=st.session_state.get("prueba_uid", 0))
    st.session_state.prueba_uid = st.session_state.get("prueba_uid", 0) + 1
