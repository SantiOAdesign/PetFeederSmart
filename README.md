# 🐾 PetFeeder/Smart

Sistema IoT multimodal para alimentar a una mascota a distancia. Un ESP32 simulado en **Wokwi** (servomotor como compuerta + LEDs de estado) se comunica por **MQTT** con una app web multipágina en **Streamlit**.

- **Simulación Wokwi:** _pega aquí el link de tu proyecto_
- **Contrato MQTT:** [`docs/MQTT_contrato.md`](docs/MQTT_contrato.md)

## Estructura

```
PetFeederSmart/
├── app/
│   ├── app.py            → punto de entrada y navegación
│   ├── config.py         → broker, tópicos, nombre de la mascota, metas
│   ├── mqtt_client.py    → conexión MQTT compartida + historial
│   ├── comandos.py       → interpreta órdenes de voz/texto
│   ├── assets/           → croquetas.mp3 (sonido al servir)
│   └── vistas/
│       ├── inicio.py
│       ├── domestico.py  → Ambiente 1: control en tiempo real
│       └── analitica.py  → Ambiente 2: historial, horarios y salud
├── wokwi/                → sketch.ino, diagram.json, libraries.txt
├── docs/                 → MQTT_contrato.md
└── requirements.txt
```

## Cómo ejecutar

1. Abre la simulación en Wokwi y dale ▶️.
2. Instala dependencias y arranca la app desde la raíz del repositorio:

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Modalidades de interacción

| Modalidad | Dónde | Ejemplo |
|---|---|---|
| Botones / slider | Modo Doméstico | Elegir 80 g y pulsar *Servir* |
| Voz | Modo Doméstico | “Oye app, dale de comer a Lucas” |
| Texto | Modo Doméstico | “sirve 80 gramos”, “rellena el contenedor” |
| Feedback | App + Wokwi | Notificación y sonido de croquetas, LED verde/rojo |

## Tecnologías

ESP32 · Wokwi · MQTT (HiveMQ público) · Python · Streamlit · paho-mqtt · Plotly
