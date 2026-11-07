/*
  PetFeeder/Smart — Firmware ESP32 (Wokwi)
  =========================================
  Broker : broker.mqttdashboard.com:1883

  Tópicos
  -------
  petfeeder/eafit/SOA/comando   (suscribe)   ← órdenes desde Streamlit
  petfeeder/eafit/SOA/estado    (publica, retenido) → estado actual del dispensador
  petfeeder/eafit/SOA/evento    (publica)    → eventos para el historial
  petfeeder/eafit/SOA/conexion  (publica, retenido, LWT) → "online" / "offline"

  Comandos (JSON)
  ---------------
  { "accion": "servir",   "gramos": 50, "origen": "voz" }
  { "accion": "rellenar" }                       → contenedor al 100 %
  { "accion": "estado" }                         → vuelve a publicar el estado

  "origen" es opcional: "voz" | "texto" | "boton" | "horario" (sirve para la analítica).

  Hardware
  --------
  Servo  GPIO 13 → compuerta del dispensador (0° cerrada, 90° abierta)
  LED verde GPIO 18 → contenedor OK (parpadea mientras sirve)
  LED rojo  GPIO 19 → alerta: contenedor bajo / vacío
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// ── WiFi ──────────────────────────────────────────
const char* ssid     = "Wokwi-GUEST";
const char* password = "";

// ── MQTT ──────────────────────────────────────────
const char* mqtt_server = "broker.mqttdashboard.com";
const int   mqtt_port   = 1883;

const char* TOPIC_COMANDO  = "petfeeder/eafit/SOA/comando";
const char* TOPIC_ESTADO   = "petfeeder/eafit/SOA/estado";
const char* TOPIC_EVENTO   = "petfeeder/eafit/SOA/evento";
const char* TOPIC_CONEXION = "petfeeder/eafit/SOA/conexion";

// ── Pines ─────────────────────────────────────────
#define PIN_LED_VERDE  18
#define PIN_LED_ROJO   19
#define PIN_SERVO      13

// ── Parámetros del dispensador ────────────────────
const int ANGULO_CERRADO   = 0;
const int ANGULO_ABIERTO   = 90;
const int CAPACIDAD_G      = 1000;  // capacidad del contenedor (simulada)
const int UMBRAL_ALERTA_PCT = 20;   // por debajo de este % se enciende la alerta
const int MS_POR_GRAMO     = 20;    // tiempo de compuerta abierta por gramo (50 g ≈ 1 s)
const int GRAMOS_MIN       = 5;
const int GRAMOS_MAX       = 200;
const unsigned long INTERVALO_ESTADO_MS = 30000;  // heartbeat del estado

// ── Estado ────────────────────────────────────────
int    nivelG          = CAPACIDAD_G;
int    ultimaPorcionG  = 0;
String ultimoOrigen    = "ninguno";
int    porcionesServidas = 0;
bool   sirviendo       = false;
unsigned long ultimoEstadoMs = 0;

// ── Objetos ───────────────────────────────────────
WiFiClient   espClient;
PubSubClient client(espClient);
Servo        compuerta;

// ─────────────────────────────────────────────────
int nivelPct() {
  return (nivelG * 100) / CAPACIDAD_G;
}

bool enAlerta() {
  return nivelPct() <= UMBRAL_ALERTA_PCT;
}

// Verde = todo bien, Rojo = contenedor bajo o vacío
void actualizarLeds() {
  if (enAlerta()) {
    digitalWrite(PIN_LED_VERDE, LOW);
    digitalWrite(PIN_LED_ROJO,  HIGH);
  } else {
    digitalWrite(PIN_LED_VERDE, HIGH);
    digitalWrite(PIN_LED_ROJO,  LOW);
  }
}

// ─────────────────────────────────────────────────
void publicarEstado() {
  StaticJsonDocument<256> doc;
  doc["nivel_g"]          = nivelG;
  doc["nivel_pct"]        = nivelPct();
  doc["alerta"]           = enAlerta();
  doc["compuerta"]        = sirviendo ? "abierta" : "cerrada";
  doc["ultima_porcion_g"] = ultimaPorcionG;
  doc["ultimo_origen"]    = ultimoOrigen;
  doc["porciones"]        = porcionesServidas;

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish(TOPIC_ESTADO, buffer, true);  // retenido: la app lo recibe al conectarse
  ultimoEstadoMs = millis();
  Serial.println("Estado → " + String(buffer));
}

void publicarEvento(const char* evento, int gramos, const String& origen, const char* detalle = nullptr) {
  StaticJsonDocument<256> doc;
  doc["evento"]  = evento;
  doc["gramos"]  = gramos;
  doc["origen"]  = origen;
  doc["nivel_g"] = nivelG;
  if (detalle) doc["detalle"] = detalle;

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish(TOPIC_EVENTO, buffer);
  Serial.println("Evento → " + String(buffer));
}

// Espera sin cortar la conexión MQTT y haciendo parpadear el LED verde
void esperarSirviendo(unsigned long ms) {
  unsigned long inicio = millis();
  bool led = false;
  unsigned long ultimoParpadeo = 0;
  while (millis() - inicio < ms) {
    if (millis() - ultimoParpadeo > 150) {
      led = !led;
      digitalWrite(PIN_LED_VERDE, led);
      ultimoParpadeo = millis();
    }
    client.loop();
    delay(10);
  }
}

// ─────────────────────────────────────────────────
void servir(int gramos, const String& origen) {
  if (sirviendo) {
    publicarEvento("error", gramos, origen, "ya_sirviendo");
    return;
  }
  if (nivelG <= 0) {
    Serial.println("→ Contenedor vacío, no se puede servir");
    publicarEvento("error", gramos, origen, "contenedor_vacio");
    publicarEstado();
    return;
  }

  gramos = constrain(gramos, GRAMOS_MIN, GRAMOS_MAX);
  if (gramos > nivelG) gramos = nivelG;  // sirve lo que quede

  Serial.printf("→ Sirviendo %d g (origen: %s)\n", gramos, origen.c_str());
  sirviendo = true;
  publicarEvento("inicio", gramos, origen);  // la app puede reproducir el sonido de croquetas aquí
  publicarEstado();

  compuerta.write(ANGULO_ABIERTO);
  esperarSirviendo((unsigned long)gramos * MS_POR_GRAMO);
  compuerta.write(ANGULO_CERRADO);

  nivelG          -= gramos;
  ultimaPorcionG   = gramos;
  ultimoOrigen     = origen;
  porcionesServidas++;
  sirviendo        = false;

  actualizarLeds();
  publicarEvento("servido", gramos, origen);
  if (enAlerta()) publicarEvento("alerta", 0, origen, nivelG <= 0 ? "contenedor_vacio" : "nivel_bajo");
  publicarEstado();
}

void rellenar() {
  nivelG = CAPACIDAD_G;
  Serial.println("→ Contenedor rellenado");
  actualizarLeds();
  publicarEvento("rellenado", 0, "app");
  publicarEstado();
}

// ─────────────────────────────────────────────────
void callback(char* topic, byte* payload, unsigned int length) {
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';
  Serial.println("Comando recibido: " + String(message));

  StaticJsonDocument<192> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (error) {
    Serial.println("Error JSON: " + String(error.c_str()));
    return;
  }

  const char* accion = doc["accion"];
  if (accion == nullptr) {
    Serial.println("Campo 'accion' no encontrado");
    return;
  }

  String origen = doc["origen"] | "app";

  if (strcmp(accion, "servir") == 0) {
    int gramos = doc["gramos"] | 50;  // 50 g por defecto
    servir(gramos, origen);
  }
  else if (strcmp(accion, "rellenar") == 0) {
    rellenar();
  }
  else if (strcmp(accion, "estado") == 0) {
    publicarEstado();
  }
  else {
    Serial.println("→ Acción no reconocida: " + String(accion));
    publicarEvento("error", 0, origen, "accion_desconocida");
  }
}

// ─────────────────────────────────────────────────
void setup_wifi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado → IP: " + WiFi.localIP().toString());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT... ");
    String clientId = "PetFeeder-" + String(random(0xffff), HEX);

    // Last Will: si el ESP32 se desconecta, el broker publica "offline"
    if (client.connect(clientId.c_str(), TOPIC_CONEXION, 0, true, "offline")) {
      Serial.println("conectado");
      client.publish(TOPIC_CONEXION, "online", true);
      client.subscribe(TOPIC_COMANDO);
      Serial.println("Suscrito a: " + String(TOPIC_COMANDO));
      publicarEstado();
    } else {
      Serial.println("falló (rc=" + String(client.state()) + ") reintentando en 5s");
      delay(5000);
    }
  }
}

// ─────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_ROJO,  OUTPUT);

  compuerta.attach(PIN_SERVO);
  compuerta.write(ANGULO_CERRADO);
  actualizarLeds();

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setBufferSize(512);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Heartbeat: publica el estado cada cierto tiempo
  if (millis() - ultimoEstadoMs > INTERVALO_ESTADO_MS) {
    publicarEstado();
  }
}
