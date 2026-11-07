# PetFeeder/Smart — Contrato MQTT

Broker: `broker.mqttdashboard.com` · Puerto `1883` (ESP32) · WebSocket `8000` si se necesita desde navegador.

| Tópico | Dirección | Retenido | Contenido |
|---|---|:---:|---|
| `petfeeder/eafit/SOA/comando` | Streamlit → ESP32 | No | Órdenes |
| `petfeeder/eafit/SOA/estado` | ESP32 → Streamlit | Sí | Estado actual del dispensador |
| `petfeeder/eafit/SOA/evento` | ESP32 → Streamlit | No | Eventos para historial/analítica |
| `petfeeder/eafit/SOA/conexion` | ESP32 → Streamlit | Sí | `online` / `offline` (Last Will) |

## Comandos (`.../comando`)

```json
{ "accion": "servir", "gramos": 50, "origen": "voz" }
{ "accion": "rellenar" }
{ "accion": "estado" }
```

- `gramos`: 5–200 (por defecto 50). Si queda menos comida, sirve lo que quede.
- `origen` (opcional): `voz` · `texto` · `boton` · `horario`. Se guarda para la analítica.

## Estado (`.../estado`)

```json
{
  "nivel_g": 850, "nivel_pct": 85, "alerta": false,
  "compuerta": "cerrada", "ultima_porcion_g": 50,
  "ultimo_origen": "voz", "porciones": 3
}
```

Se publica al conectar, después de cada acción y cada 30 s.

## Eventos (`.../evento`)

```json
{ "evento": "servido", "gramos": 50, "origen": "voz", "nivel_g": 850 }
```

| `evento` | Cuándo | Uso en la app |
|---|---|---|
| `inicio` | Se abre la compuerta | Sonido de croquetas + vibración |
| `servido` | Se cierra la compuerta | Registrar en el historial |
| `alerta` | Nivel ≤ 20 % (`detalle`: `nivel_bajo` / `contenedor_vacio`) | Notificación |
| `rellenado` | Contenedor al 100 % | Historial |
| `error` | `detalle`: `contenedor_vacio`, `ya_sirviendo`, `accion_desconocida` | Mensaje al usuario |

El ESP32 no tiene reloj: **Streamlit le pone la hora** a cada evento al recibirlo.

## LEDs

| Situación | Verde (GPIO 18) | Rojo (GPIO 19) |
|---|:---:|:---:|
| Nivel > 20 % | Encendido | Apagado |
| Sirviendo | Parpadea | — |
| Nivel ≤ 20 % o vacío | Apagado | Encendido |

## Prueba rápida sin la app

En [HiveMQ WebSocket Client](https://www.hivemq.com/demos/websocket-client/) conectar al broker, suscribirse a `petfeeder/eafit/SOA/#` y publicar en `petfeeder/eafit/SOA/comando`:
`{"accion":"servir","gramos":100,"origen":"texto"}`
