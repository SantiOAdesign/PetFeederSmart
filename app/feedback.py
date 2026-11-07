"""
Feedback sonoro y háptico en el navegador.

Inyecta un pequeño script que se ejecuta en la página principal (window.parent),
así el sonido sigue sonando aunque Streamlit vuelva a dibujar la página.

- "inicio"  → sonido de croquetas cayendo + vibración corta repetida
- "servido" → vibración corta
- "alerta" / "error" → pitido de dos tonos + vibración larga

La vibración usa navigator.vibrate: funciona en Chrome para Android
(no en iPhone ni en computador).
"""

import base64
import json
from functools import lru_cache
from pathlib import Path

import streamlit.components.v1 as components

ASSETS = Path(__file__).parent / "assets"

VIBRACION = {
    "inicio": [80, 40, 80, 40, 80, 40, 80],
    "servido": [150],
    "alerta": [300, 120, 300],
    "error": [400],
    "prueba": [80, 40, 80, 40, 80, 40, 80],
}

_PITIDO_JS = """
const C = p.AudioContext || p.webkitAudioContext;
if (C) {
  const ctx = p.__pfCtx || (p.__pfCtx = new C());
  [[0, 880], [0.25, 620]].forEach(([t, f]) => {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.value = f;
    g.gain.setValueAtTime(0.18, ctx.currentTime + t);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.22);
    o.connect(g).connect(ctx.destination);
    o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.22);
  });
}
"""


@lru_cache(maxsize=1)
def _sonido_croquetas() -> str | None:
    """Usa assets/croquetas.mp3 si existe; si no, el .wav incluido."""
    for nombre, mime in (("croquetas.mp3", "audio/mpeg"), ("croquetas.wav", "audio/wav")):
        ruta = ASSETS / nombre
        if ruta.exists():
            return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()
    return None


def reproducir(evento: str, sonido: bool = True, vibracion: bool = True, uid: int = 0) -> None:
    js = []
    if sonido and evento in ("inicio", "prueba"):
        src = _sonido_croquetas()
        if src:
            js.append(f"p.__pfAudio = new p.Audio('{src}'); p.__pfAudio.play().catch(() => {{}});")
    if sonido and evento in ("alerta", "error"):
        js.append(_PITIDO_JS)
    if vibracion and evento in VIBRACION:
        js.append(f"if (p.navigator.vibrate) p.navigator.vibrate({json.dumps(VIBRACION[evento])});")
    if not js:
        return

    # uid hace que cada evento genere un script distinto y se vuelva a ejecutar
    html = (
        f"<script>/* evento {uid} */(function () {{ const p = window.parent; "
        f"try {{ {''.join(js)} }} catch (e) {{ console.log('PetFeeder feedback:', e); }} }})();</script>"
    )
    components.html(html, height=0)
