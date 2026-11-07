"""
Perfil de la mascota: nombre, porciones y preferencias de feedback.

Se guarda en perfil.json junto a la app, así que es el mismo para todos los
que abran la app (un dispensador = una mascota). Los valores por defecto
vienen de config.py.
"""

import json
from pathlib import Path

import config

PERFIL_JSON = Path(__file__).parent / "perfil.json"

DEFAULTS = {
    "nombre": config.NOMBRE_MASCOTA,
    "gramos_defecto": config.GRAMOS_DEFECTO,
    "meta_diaria_g": config.META_DIARIA_G,
    "sonido": True,
    "vibracion": True,
}


def cargar() -> dict:
    datos = dict(DEFAULTS)
    if PERFIL_JSON.exists():
        try:
            datos.update(json.loads(PERFIL_JSON.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    return datos


def guardar(datos: dict) -> None:
    limpio = {k: datos.get(k, v) for k, v in DEFAULTS.items()}
    limpio["nombre"] = str(limpio["nombre"]).strip() or DEFAULTS["nombre"]
    PERFIL_JSON.write_text(json.dumps(limpio, ensure_ascii=False, indent=2), encoding="utf-8")
