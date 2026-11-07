"""Configuración general de PetFeeder/Smart."""

from zoneinfo import ZoneInfo

# ── MQTT (debe coincidir con el firmware del ESP32) ──────────
BROKER = "broker.mqttdashboard.com"
PORT = 1883
BASE_TOPIC = "petfeeder/eafit/SOA"

TOPIC_COMANDO = f"{BASE_TOPIC}/comando"
TOPIC_ESTADO = f"{BASE_TOPIC}/estado"
TOPIC_EVENTO = f"{BASE_TOPIC}/evento"
TOPIC_CONEXION = f"{BASE_TOPIC}/conexion"

# ── Mascota ──────────────────────────────────────────────────
NOMBRE_MASCOTA = "Lucas"
GRAMOS_DEFECTO = 50       # porción cuando no se dice cuánto
META_DIARIA_G = 300       # ración diaria recomendada (para la analítica)

# ── Otros ────────────────────────────────────────────────────
ZONA_HORARIA = ZoneInfo("America/Bogota")
