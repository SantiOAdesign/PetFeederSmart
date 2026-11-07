"""
Interpreta frases en lenguaje natural (voz o texto) y las convierte en comandos
para el dispensador.

Ejemplos:
    "Oye app, dale de comer a Lucas"  → servir 50 g
    "sirve 80 gramos"                 → servir 80 g
    "dale doble porción"              → servir 100 g
    "rellena el contenedor"           → rellenar
    "¿cuánta comida queda?"           → estado
"""

import re
import unicodedata

from config import GRAMOS_DEFECTO

PALABRAS_RELLENAR = ["rellena", "rellenar", "recarga", "recargar", "llena el contenedor", "llenar el contenedor"]
PALABRAS_ESTADO = ["estado", "cuanta comida", "cuanto queda", "queda comida", "nivel", "como esta", "lleno", "vacio"]
PALABRAS_SERVIR = ["comer", "comida", "servir", "sirve", "sirvele", "alimenta", "dale", "croqueta", "porcion", "hambre"]


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def interpretar(texto: str, gramos_defecto: int = GRAMOS_DEFECTO) -> dict | None:
    """Devuelve un comando {"accion": ..., ...} o None si no se entendió."""
    if not texto:
        return None
    t = _normalizar(texto)

    if any(p in t for p in PALABRAS_RELLENAR):
        return {"accion": "rellenar"}

    if any(p in t for p in PALABRAS_ESTADO):
        return {"accion": "estado"}

    if any(p in t for p in PALABRAS_SERVIR):
        match = re.search(r"(\d+)\s*(g\b|gr\b|gramos)?", t)
        if match:
            gramos = int(match.group(1))
        elif "doble" in t:
            gramos = gramos_defecto * 2
        elif any(p in t for p in ["poquito", "poco", "media"]):
            gramos = gramos_defecto // 2
        else:
            gramos = gramos_defecto
        return {"accion": "servir", "gramos": max(5, min(200, gramos))}

    return None
