"""
Estilo visual de PetFeeder/Smart: CSS global, encabezados, tarjetas y
plantilla para los gráficos de Plotly. El tema base (colores) está en
.streamlit/config.toml en la raíz del repositorio.
"""

from html import escape

import streamlit as st

# ── Paleta ───────────────────────────────────────────────────
NARANJA = "#E8743B"
NARANJA_OSCURO = "#C25A26"
CREMA = "#FFFAF4"
ARENA = "#FBEFE3"
CAFE = "#2B2118"
GRIS = "#7A6A5E"
VERDE = "#3E9B6E"
AMBAR = "#E0A526"
ROJO = "#D9534F"
SERIES = [NARANJA, "#4F8A8B", AMBAR, "#9A6FB0", VERDE, "#C9785D"]

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea {{
  font-family: 'Nunito', system-ui, sans-serif !important;
}}
h1, h2, h3, h4 {{ font-family: 'Nunito', system-ui, sans-serif !important; font-weight: 800 !important;
  color: {CAFE}; letter-spacing: -0.01em; }}

.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; }}

/* Barra lateral */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #FFF3E8 0%, {ARENA} 100%);
  border-right: 1px solid #F1DFCD;
}}
[data-testid="stSidebarNav"] a {{ border-radius: 12px; }}

/* Contenedores con borde → tarjetas suaves */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{
  border-radius: 18px;
}}
div[data-testid="stForm"] {{
  background: #FFFFFF; border: 1px solid #F1DFCD; border-radius: 18px;
  box-shadow: 0 4px 18px rgba(120, 72, 30, 0.06);
}}

/* Botones */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  border-radius: 999px; font-weight: 700; padding: 0.55rem 1.3rem;
  transition: transform .12s ease, box-shadow .12s ease;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover {{
  transform: translateY(-1px); box-shadow: 0 6px 16px rgba(232, 116, 59, 0.25);
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
  background: linear-gradient(135deg, {NARANJA} 0%, {NARANJA_OSCURO} 100%); border: none;
}}

/* Pestañas tipo "pastilla" */
.stTabs [role="tablist"] {{
  gap: 6px; background: {ARENA}; padding: 6px; border-radius: 999px; width: fit-content;
  border: none !important; box-shadow: none !important;
}}
.stTabs [role="tab"] {{
  border-radius: 999px; padding: 6px 18px !important; height: auto; font-weight: 700;
  border: none !important; background: transparent;
}}
.stTabs [role="tab"][aria-selected="true"] {{ background: #FFFFFF; box-shadow: 0 2px 8px rgba(120,72,30,.12); }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
.stTabs [role="tablist"]::after, .stTabs .react-aria-SelectionIndicator {{ display: none !important; }}

/* Métricas nativas */
[data-testid="stMetric"] {{
  background: #FFFFFF; border: 1px solid #F1DFCD; border-radius: 18px;
  padding: 16px 18px; box-shadow: 0 4px 18px rgba(120, 72, 30, 0.06);
}}
[data-testid="stMetricLabel"] p {{ color: {GRIS}; font-weight: 700; }}
[data-testid="stMetricValue"] {{ color: {CAFE}; font-weight: 800; }}

/* Alertas y tablas */
[data-testid="stAlert"] {{ border-radius: 14px; }}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{ border-radius: 14px; overflow: hidden; }}
hr {{ margin: 1.6rem 0 !important; border-color: #F1DFCD !important; }}

/* ── Componentes propios ── */
.pf-hero {{
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, {NARANJA} 0%, #F39A5B 55%, #F7C08A 100%);
  color: #FFFFFF; border-radius: 24px; padding: 28px 32px; margin-bottom: 1.4rem;
  box-shadow: 0 10px 30px rgba(232, 116, 59, 0.28);
}}
.pf-hero h1 {{ color: #FFFFFF !important; margin: 0 0 4px 0; padding: 0; font-size: 2.1rem; }}
.pf-hero p {{ margin: 0; font-size: 1.05rem; opacity: .95; }}
.pf-hero .pf-hero-icono {{ position: absolute; right: 22px; bottom: -18px; font-size: 7rem; opacity: .22; }}

.pf-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 1rem; }}
.pf-card {{
  background: #FFFFFF; border: 1px solid #F1DFCD; border-radius: 20px; padding: 18px 20px;
  box-shadow: 0 4px 18px rgba(120, 72, 30, 0.06); height: 100%;
}}
.pf-card .pf-et {{ display: flex; align-items: center; gap: 8px; color: {GRIS};
  font-weight: 700; font-size: .9rem; text-transform: uppercase; letter-spacing: .04em; }}
.pf-card .pf-ic {{ width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center;
  font-size: 1.15rem; background: {ARENA}; }}
.pf-card .pf-val {{ font-size: 2rem; font-weight: 800; color: {CAFE}; margin: 10px 0 2px 0; line-height: 1.1; }}
.pf-card .pf-det {{ color: {GRIS}; font-size: .9rem; }}

.pf-barra {{ height: 12px; background: {ARENA}; border-radius: 999px; overflow: hidden; margin: 10px 0 6px 0; }}
.pf-barra > div {{ height: 100%; border-radius: 999px; transition: width .6s ease; }}

.pf-punto {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }}
.pf-pulso {{ animation: pf-pulso 1.2s infinite; }}
@keyframes pf-pulso {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,155,110,.6); }}
  100% {{ box-shadow: 0 0 0 10px rgba(62,155,110,0); }} }}

.pf-chip {{ display: flex; align-items: center; justify-content: space-between;
  background: #FFFFFF; border: 1px solid #F1DFCD; border-radius: 12px;
  padding: 8px 12px; margin: 6px 0; font-weight: 600; font-size: .92rem; }}
.pf-chip .pf-ok {{ color: {VERDE}; }} .pf-chip .pf-no {{ color: {ROJO}; }}

.pf-mascota {{ display: flex; align-items: center; gap: 12px; margin: 4px 0 10px 0; }}
.pf-avatar {{ width: 48px; height: 48px; border-radius: 50%; display: grid; place-items: center;
  font-size: 1.6rem; background: linear-gradient(135deg, {NARANJA}, #F7C08A); }}
.pf-mascota b {{ font-size: 1.15rem; color: {CAFE}; }}
.pf-mascota span {{ display: block; color: {GRIS}; font-size: .82rem; }}

.pf-ejemplo {{ display: inline-block; background: #FFFFFF; border: 1px dashed {NARANJA};
  color: {NARANJA_OSCURO}; border-radius: 999px; padding: 6px 14px; margin: 4px 6px 4px 0;
  font-weight: 600; }}
.pf-seccion {{ font-weight: 800; font-size: 1.25rem; color: {CAFE}; margin: 1.2rem 0 .6rem 0; }}
</style>
"""


def aplicar() -> None:
    """Inyecta el CSS global. Llamar una vez por ejecución (en app.py)."""
    st.html(_CSS)


def encabezado(icono: str, titulo: str, subtitulo: str = "") -> None:
    st.html(
        f'<div class="pf-hero"><h1>{icono} {escape(titulo)}</h1>'
        f'<p>{escape(subtitulo)}</p><div class="pf-hero-icono">{icono}</div></div>'
    )


def seccion(texto: str) -> None:
    st.html(f'<div class="pf-seccion">{escape(texto)}</div>')


def tarjeta(icono: str, etiqueta: str, valor: str, detalle: str = "", extra_html: str = "") -> str:
    """Devuelve el HTML de una tarjeta; agrupar varias con grilla()."""
    return (
        f'<div class="pf-card"><div class="pf-et"><div class="pf-ic">{icono}</div>{escape(etiqueta)}</div>'
        f'<div class="pf-val">{valor}</div>{extra_html}<div class="pf-det">{detalle}</div></div>'
    )


def grilla(*tarjetas: str) -> None:
    st.html(f'<div class="pf-grid">{"".join(tarjetas)}</div>')


def barra(pct: float) -> str:
    pct = max(0.0, min(100.0, float(pct)))
    color = VERDE if pct > 50 else AMBAR if pct > 20 else ROJO
    return f'<div class="pf-barra"><div style="width:{pct:.0f}%;background:{color}"></div></div>'


def punto(color: str, pulso: bool = False) -> str:
    return f'<span class="pf-punto{" pf-pulso" if pulso else ""}" style="background:{color}"></span>'


def chip_estado(etiqueta: str, ok: bool) -> str:
    estado = '<span class="pf-ok">● En línea</span>' if ok else '<span class="pf-no">● Sin conexión</span>'
    return f'<div class="pf-chip"><span>{escape(etiqueta)}</span>{estado}</div>'


def ejemplos(frases: list[str]) -> None:
    st.html("".join(f'<span class="pf-ejemplo">“{escape(f)}”</span>' for f in frases))


def figura(fig, titulo: str | None = None):
    """Aplica el estilo de la app a un gráfico de Plotly."""
    fig.update_layout(
        title=dict(text=titulo or fig.layout.title.text, font=dict(size=16, color=CAFE, family="Nunito")),
        font=dict(family="Nunito, sans-serif", color=GRIS),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        colorway=SERIES,
        margin=dict(l=10, r=10, t=50, b=10),
        hoverlabel=dict(bgcolor="#FFFFFF", font_family="Nunito"),
        legend=dict(orientation="h", y=-0.15),
        barcornerradius=6,
    )
    fig.update_xaxes(showgrid=False, linecolor="#F1DFCD")
    fig.update_yaxes(gridcolor="#F5E8DA", zeroline=False)
    fig.update_traces(marker_line_width=0, selector=dict(type="bar"))
    return fig
