"""Ambiente 2 — Analítica y Gestión de Salud: hábitos, horarios automáticos e historial."""

from datetime import datetime, time

import pandas as pd
import plotly.express as px
import streamlit as st

import estilo
import perfil
from config import MAX_HORARIOS, ZONA_HORARIA
from mqtt_client import get_mqtt

mq = get_mqtt()
datos = perfil.cargar()
NOMBRE_MASCOTA = datos["nombre"]
META_DIARIA_G = int(datos["meta_diaria_g"])
GRAMOS_DEFECTO = int(datos["gramos_defecto"])

estilo.encabezado("📊", "Analítica y Salud", f"Hábitos, horarios y historial de alimentación de {NOMBRE_MASCOTA}.")

df = mq.historial_df()
comidas = df[df["evento"] == "servido"].copy() if not df.empty else pd.DataFrame()

tab_resumen, tab_horarios, tab_historial = st.tabs(["📈 Resumen", "⏰ Horarios", "📋 Historial"])


# ══ Resumen ══════════════════════════════════════════════════
with tab_resumen:
    if comidas.empty:
        st.info("Aún no hay comidas registradas. Sirve comida desde el Modo Doméstico "
                "o programa un horario y aquí aparecerán los datos.")
    else:
        comidas["fecha"] = comidas["hora"].dt.date
        comidas["hora_dia"] = comidas["hora"].dt.hour
        hoy = datetime.now(ZONA_HORARIA).date()
        comidas_hoy = comidas[comidas["fecha"] == hoy]

        total_hoy = int(comidas_hoy["gramos"].sum())
        ultima = comidas["hora"].max()
        minutos = int((datetime.now(ZONA_HORARIA) - ultima).total_seconds() // 60)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Comida hoy", f"{total_hoy} g")
        c2.metric("Porciones hoy", len(comidas_hoy))
        c3.metric("Porción promedio", f"{comidas['gramos'].mean():.0f} g")
        c4.metric("Última comida", f"hace {minutos} min" if minutos < 120 else f"{ultima:%d/%m %H:%M}")

        st.markdown(f"**Ración diaria recomendada:** {META_DIARIA_G} g · se cambia en *Mi mascota*")
        st.progress(min(total_hoy / META_DIARIA_G, 1.0), text=f"{total_hoy} / {META_DIARIA_G} g")
        if total_hoy > META_DIARIA_G:
            st.warning(f"{NOMBRE_MASCOTA} ya superó la ración diaria recomendada.", icon="⚠️")

        estilo.seccion("Tendencias")
        g1, g2 = st.columns(2)
        with g1:
            por_dia = comidas.groupby("fecha", as_index=False)["gramos"].sum()
            fig = px.bar(por_dia, x="fecha", y="gramos", title="Comida por día (g)")
            fig.add_hline(y=META_DIARIA_G, line_dash="dash", line_color=estilo.VERDE,
                          annotation_text="Meta diaria", annotation_font_color=estilo.VERDE)
            st.plotly_chart(estilo.figura(fig), width="stretch")
        with g2:
            por_hora = comidas.groupby("hora_dia", as_index=False)["gramos"].sum()
            fig = px.bar(por_hora, x="hora_dia", y="gramos", title="Horarios de comida",
                         labels={"hora_dia": "Hora del día"})
            fig.update_xaxes(range=[-0.5, 23.5], dtick=2)
            st.plotly_chart(estilo.figura(fig), width="stretch")

        g3, g4 = st.columns(2)
        with g3:
            por_origen = comidas["origen"].value_counts().reset_index()
            por_origen.columns = ["origen", "veces"]
            fig = px.pie(por_origen, names="origen", values="veces", title="¿Cómo se dio la orden?", hole=0.55)
            fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#FFFFFF", width=3)))
            st.plotly_chart(estilo.figura(fig), width="stretch")
        with g4, st.container(border=True):
            st.markdown("#### 🐾 Hábitos")
            hora_pico = int(por_hora.loc[por_hora["gramos"].idxmax(), "hora_dia"])
            dias = comidas["fecha"].nunique()
            programadas = int((comidas["origen"] == "horario").sum())
            st.write(f"- Hora en la que más come: **{hora_pico}:00**")
            st.write(f"- Promedio diario: **{comidas['gramos'].sum() / dias:.0f} g** ({dias} día(s) con registro)")
            st.write(f"- Modalidad más usada: **{por_origen.iloc[0]['origen']}**")
            st.write(f"- Comidas automáticas por horario: **{programadas}** de {len(comidas)}")
            st.write(f"- Alertas de contenedor bajo: **{len(df[df['evento'] == 'alerta'])}**")


# ══ Horarios automáticos ═════════════════════════════════════
with tab_horarios:
    estilo.seccion("Horarios automáticos")
    st.caption("Los horarios se guardan en el dispensador: sirve a la hora indicada "
               "aunque la app esté cerrada. Hora de Colombia.")

    s = mq.snapshot()
    estado = s["estado"]
    if s["esp32_online"] and "horarios" in estado:
        texto = f"El dispensador tiene **{estado['horarios']}** horario(s) cargado(s)"
        if estado.get("proximo"):
            texto += f" · próxima comida a las **{estado['proximo']}** ({estado.get('proximo_g')} g)"
        if estado.get("hora"):
            texto += f" · hora del dispensador: {estado['hora']}"
        st.success(texto, icon="⏰")
    elif not s["esp32_online"]:
        st.warning("El dispensador no está conectado. Puedes guardar los horarios igual: "
                   "los recibirá al conectarse.", icon="🔌")

    def a_tabla(horarios: list[dict]) -> pd.DataFrame:
        filas = []
        for h in horarios:
            try:
                hh, mm = map(int, str(h["hora"]).split(":"))
                filas.append({"activo": bool(h.get("activo", True)), "hora": time(hh, mm),
                              "gramos": int(h.get("gramos", GRAMOS_DEFECTO))})
            except (ValueError, KeyError):
                continue
        if not filas:  # sugerencia inicial
            filas = [{"activo": True, "hora": time(8, 0), "gramos": GRAMOS_DEFECTO},
                     {"activo": True, "hora": time(13, 0), "gramos": GRAMOS_DEFECTO},
                     {"activo": True, "hora": time(19, 0), "gramos": GRAMOS_DEFECTO}]
        return pd.DataFrame(filas, columns=["activo", "hora", "gramos"])

    tabla = st.data_editor(
        a_tabla(s["horarios"]),
        key="editor_horarios",
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "activo": st.column_config.CheckboxColumn("Activo", default=True),
            "hora": st.column_config.TimeColumn("Hora", format="HH:mm", step=60, required=True),
            "gramos": st.column_config.NumberColumn("Gramos", min_value=5, max_value=200, step=5,
                                                    default=GRAMOS_DEFECTO, required=True),
        },
    )

    # Validación: sin filas vacías, sin horas repetidas, máximo MAX_HORARIOS
    validos = tabla.dropna(subset=["hora", "gramos"]).drop_duplicates(subset=["hora"])
    validos = validos.sort_values("hora").head(MAX_HORARIOS)
    total_programado = int(validos.loc[validos["activo"].fillna(True).astype(bool), "gramos"].sum())

    c1, c2 = st.columns([2, 1])
    with c1:
        st.caption(f"Total programado al día: **{total_programado} g** de {META_DIARIA_G} g recomendados")
        if total_programado > META_DIARIA_G:
            st.warning(f"Los horarios superan la ración diaria de {NOMBRE_MASCOTA}.", icon="⚠️")
        if len(tabla.dropna(subset=["hora"])) > MAX_HORARIOS:
            st.info(f"El dispensador guarda máximo {MAX_HORARIOS} horarios; se enviarán los primeros {MAX_HORARIOS}.")
    with c2:
        if st.button("💾 Guardar en el dispensador", type="primary", width="stretch"):
            lista = [{"hora": h.strftime("%H:%M"), "gramos": int(g), "activo": bool(a) if pd.notna(a) else True}
                     for a, h, g in validos[["activo", "hora", "gramos"]].itertuples(index=False)]
            if mq.publicar_horarios(lista):
                st.success(f"{len(lista)} horario(s) enviados al dispensador.")
            else:
                st.error("No hay conexión con el broker MQTT. Intenta de nuevo en unos segundos.")


# ══ Historial ════════════════════════════════════════════════
with tab_historial:
    if df.empty:
        st.info("Todavía no hay eventos registrados.")
    else:
        tabla_hist = df.sort_values("hora", ascending=False).copy()
        tabla_hist["hora"] = tabla_hist["hora"].dt.strftime("%d/%m/%Y %H:%M:%S")
        st.dataframe(tabla_hist, width="stretch", hide_index=True)
        st.download_button("⬇️ Descargar historial (CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name="historial_petfeeder.csv", mime="text/csv")
