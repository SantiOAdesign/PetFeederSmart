"""Ambiente 2 — Analítica y Gestión de Salud."""

from datetime import datetime

import plotly.express as px
import streamlit as st

from config import META_DIARIA_G, NOMBRE_MASCOTA, ZONA_HORARIA
from mqtt_client import get_mqtt

mq = get_mqtt()

st.title("📊 Analítica y Salud")
st.caption(f"Historial y hábitos de alimentación de {NOMBRE_MASCOTA}.")

df = mq.historial_df()
comidas = df[df["evento"] == "servido"].copy() if not df.empty else df

if comidas.empty:
    st.info("Aún no hay comidas registradas. Sirve comida desde el Modo Doméstico "
            "y aquí aparecerá el historial.")
    st.stop()

comidas["fecha"] = comidas["hora"].dt.date
comidas["hora_dia"] = comidas["hora"].dt.hour
hoy = datetime.now(ZONA_HORARIA).date()
comidas_hoy = comidas[comidas["fecha"] == hoy]

# ── Resumen del día ──────────────────────────────────────────
total_hoy = int(comidas_hoy["gramos"].sum())
ultima = comidas["hora"].max()
minutos = int((datetime.now(ZONA_HORARIA) - ultima).total_seconds() // 60)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Comida hoy", f"{total_hoy} g")
c2.metric("Porciones hoy", len(comidas_hoy))
c3.metric("Porción promedio", f"{comidas['gramos'].mean():.0f} g")
c4.metric("Última comida", f"hace {minutos} min" if minutos < 120 else f"{ultima:%d/%m %H:%M}")

st.markdown(f"**Ración diaria recomendada:** {META_DIARIA_G} g")
st.progress(min(total_hoy / META_DIARIA_G, 1.0), text=f"{total_hoy} / {META_DIARIA_G} g")
if total_hoy > META_DIARIA_G:
    st.warning(f"{NOMBRE_MASCOTA} ya superó la ración diaria recomendada.", icon="⚠️")

st.divider()

# ── Gráficas ─────────────────────────────────────────────────
g1, g2 = st.columns(2)
with g1:
    por_dia = comidas.groupby("fecha", as_index=False)["gramos"].sum()
    fig = px.bar(por_dia, x="fecha", y="gramos", title="Comida por día (g)")
    fig.add_hline(y=META_DIARIA_G, line_dash="dash", annotation_text="Meta diaria")
    st.plotly_chart(fig, use_container_width=True)
with g2:
    por_hora = comidas.groupby("hora_dia", as_index=False)["gramos"].sum()
    fig = px.bar(por_hora, x="hora_dia", y="gramos", title="Horarios de comida",
                 labels={"hora_dia": "Hora del día"})
    fig.update_xaxes(range=[-0.5, 23.5], dtick=2)
    st.plotly_chart(fig, use_container_width=True)

g3, g4 = st.columns(2)
with g3:
    por_origen = comidas["origen"].value_counts().reset_index()
    por_origen.columns = ["origen", "veces"]
    fig = px.pie(por_origen, names="origen", values="veces", title="¿Cómo se dio la orden?", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)
with g4:
    st.markdown("**Hábitos**")
    hora_pico = int(por_hora.loc[por_hora["gramos"].idxmax(), "hora_dia"])
    dias = comidas["fecha"].nunique()
    st.write(f"- Hora en la que más come: **{hora_pico}:00**")
    st.write(f"- Promedio diario: **{comidas['gramos'].sum() / dias:.0f} g** ({dias} día(s) con registro)")
    st.write(f"- Modalidad más usada: **{por_origen.iloc[0]['origen']}**")
    alertas = df[df["evento"] == "alerta"]
    st.write(f"- Alertas de contenedor bajo: **{len(alertas)}**")

st.divider()

# ── Historial ────────────────────────────────────────────────
st.subheader("Historial de eventos")
tabla = df.sort_values("hora", ascending=False).copy()
tabla["hora"] = tabla["hora"].dt.strftime("%d/%m/%Y %H:%M:%S")
st.dataframe(tabla, use_container_width=True, hide_index=True)
st.download_button("⬇️ Descargar historial (CSV)", df.to_csv(index=False).encode("utf-8"),
                   file_name="historial_petfeeder.csv", mime="text/csv")
