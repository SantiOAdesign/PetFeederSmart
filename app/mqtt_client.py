"""
Conexión MQTT compartida por todas las páginas.

El cliente corre en un hilo propio (loop_start) y guarda el último estado del
ESP32 y el historial de eventos. Se crea una sola vez gracias a
st.cache_resource, así que no se reconecta en cada rerun de Streamlit.
"""

import csv
import json
import threading
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path

import pandas as pd
import paho.mqtt.client as mqtt
import streamlit as st

import config

HISTORIAL_CSV = Path(__file__).parent / "historial.csv"
CAMPOS_CSV = ["hora", "evento", "gramos", "origen", "nivel_g", "detalle"]


class PetFeederMQTT:
    def __init__(self):
        self._lock = threading.Lock()
        self.estado: dict = {}
        self.horarios: list = []           # último horario publicado (retenido en el broker)
        self.esp32_online = False
        self.broker_conectado = False
        self.eventos: deque = deque(maxlen=1000)
        self.contador_eventos = 0          # sube con cada evento nuevo
        self.ultima_actualizacion = None

        self._cargar_historial()

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"petfeeder-app-{uuid.uuid4().hex[:8]}",
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.connect_async(config.BROKER, config.PORT, keepalive=30)
        self.client.loop_start()

    # ── Callbacks (corren en el hilo de MQTT) ────────────────
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            return
        self.broker_conectado = True
        client.subscribe(f"{config.BASE_TOPIC}/#")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.broker_conectado = False

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode(errors="ignore")
        ahora = datetime.now(config.ZONA_HORARIA)

        with self._lock:
            if msg.topic == config.TOPIC_CONEXION:
                self.esp32_online = payload.strip() == "online"

            elif msg.topic == config.TOPIC_ESTADO:
                try:
                    self.estado = json.loads(payload)
                    self.esp32_online = True
                    self.ultima_actualizacion = ahora
                except json.JSONDecodeError:
                    pass

            elif msg.topic == config.TOPIC_HORARIOS:
                try:
                    self.horarios = json.loads(payload).get("horarios", [])
                except (json.JSONDecodeError, AttributeError):
                    pass

            elif msg.topic == config.TOPIC_EVENTO:
                try:
                    datos = json.loads(payload)
                except json.JSONDecodeError:
                    return
                evento = {
                    "hora": ahora,
                    "evento": datos.get("evento", ""),
                    "gramos": datos.get("gramos", 0),
                    "origen": datos.get("origen", ""),
                    "nivel_g": datos.get("nivel_g"),
                    "detalle": datos.get("detalle", ""),
                }
                self.eventos.append(evento)
                self.contador_eventos += 1
                self._guardar_evento(evento)

    # ── Historial en CSV (para que la analítica sobreviva reinicios) ──
    def _cargar_historial(self):
        if not HISTORIAL_CSV.exists():
            return
        with open(HISTORIAL_CSV, newline="", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                try:
                    fila["hora"] = datetime.fromisoformat(fila["hora"])
                    fila["gramos"] = int(float(fila["gramos"] or 0))
                    fila["nivel_g"] = int(float(fila["nivel_g"])) if fila["nivel_g"] else None
                    self.eventos.append(fila)
                except (ValueError, KeyError):
                    continue

    def _guardar_evento(self, evento: dict):
        nuevo = not HISTORIAL_CSV.exists()
        with open(HISTORIAL_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
            if nuevo:
                w.writeheader()
            w.writerow({**evento, "hora": evento["hora"].isoformat()})

    # ── Comandos hacia el ESP32 ──────────────────────────────
    def publicar(self, comando: dict) -> bool:
        if not self.broker_conectado:
            return False
        info = self.client.publish(config.TOPIC_COMANDO, json.dumps(comando))
        return info.rc == mqtt.MQTT_ERR_SUCCESS

    def servir(self, gramos: int, origen: str) -> bool:
        return self.publicar({"accion": "servir", "gramos": int(gramos), "origen": origen})

    def rellenar(self) -> bool:
        return self.publicar({"accion": "rellenar"})

    def pedir_estado(self) -> bool:
        return self.publicar({"accion": "estado"})

    def publicar_horarios(self, horarios: list[dict]) -> bool:
        """Envía los horarios al ESP32. Se publican retenidos para que el
        dispensador los recupere si se reinicia o se reconecta."""
        if not self.broker_conectado:
            return False
        info = self.client.publish(config.TOPIC_HORARIOS, json.dumps({"horarios": horarios}), retain=True)
        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            with self._lock:
                self.horarios = horarios
            return True
        return False

    # ── Lectura segura desde las páginas ─────────────────────
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "estado": dict(self.estado),
                "horarios": list(self.horarios),
                "esp32_online": self.esp32_online,
                "broker_conectado": self.broker_conectado,
                "eventos": list(self.eventos),
                "contador_eventos": self.contador_eventos,
                "ultima_actualizacion": self.ultima_actualizacion,
            }

    def historial_df(self) -> pd.DataFrame:
        with self._lock:
            df = pd.DataFrame(list(self.eventos), columns=CAMPOS_CSV)
        if not df.empty:
            df["hora"] = pd.to_datetime(df["hora"], utc=True).dt.tz_convert(config.ZONA_HORARIA)
        return df


@st.cache_resource
def get_mqtt() -> PetFeederMQTT:
    """Devuelve el único cliente MQTT de la app."""
    return PetFeederMQTT()
