/*
 * Smart Door AI - ESP32 firmware
 * Libraries (Library Manager): PubSubClient, ArduinoJson (v6.x)
 * Board: "ESP32 Dev Module"
 *
 * MQTT contract
 *   subscribe : smartdoor/<DEVICE_ID>/cmd        {"action":"unlock","duration":5} | {"action":"lock"}
 *   publish   : smartdoor/<DEVICE_ID>/status     {"state":"locked|unlocked","door":"open|closed","fw":"1.0"}
 *   publish   : smartdoor/<DEVICE_ID>/heartbeat  every 10 s
 * FAIL-SECURE: boots locked, relocks locally by timer even if Wi-Fi/MQTT dies.
 */
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ---- CONFIG ----
const char* WIFI_SSID   = "YOUR_WIFI";
const char* WIFI_PASS   = "YOUR_PASSWORD";
const char* MQTT_HOST   = "192.168.1.10";   // PC / server running Mosquitto
const int   MQTT_PORT   = 1883;
const char* DEVICE_ID   = "door01";         // must match MQTT_DEVICE_ID in backend .env
const char* FW_VERSION  = "1.0";

#define RELAY_PIN   26   // relay IN  (drives the solenoid via isolated relay + flyback diode)
#define LED_PIN     2    // status LED (on = unlocked)
#define BUZZER_PIN  27
#define REED_PIN    25   // magnetic door sensor to GND (INPUT_PULLUP)
#define RELAY_ACTIVE_LOW true   // most relay modules trigger on LOW

WiFiClient wifi;
PubSubClient mqtt(wifi);
String topicCmd, topicStatus, topicBeat;

bool unlocked = false;
unsigned long relockAt = 0, lastBeat = 0, lastReconnect = 0;
bool lastDoorOpen = false;

void relay(bool on) { digitalWrite(RELAY_PIN, (on ^ RELAY_ACTIVE_LOW) ? HIGH : LOW); }

void beep(int ms) { digitalWrite(BUZZER_PIN, HIGH); delay(ms); digitalWrite(BUZZER_PIN, LOW); }

void publishStatus() {
  StaticJsonDocument<160> d;
  d["state"] = unlocked ? "unlocked" : "locked";
  d["door"]  = digitalRead(REED_PIN) == HIGH ? "open" : "closed";
  d["fw"]    = FW_VERSION;
  char buf[160];
  serializeJson(d, buf);
  mqtt.publish(topicStatus.c_str(), buf, true);
}

void setLock(bool open, unsigned long durationMs = 0) {
  unlocked = open;
  relay(open);
  digitalWrite(LED_PIN, open ? HIGH : LOW);
  relockAt = open ? millis() + durationMs : 0;
  beep(open ? 120 : 40);
  if (mqtt.connected()) publishStatus();
}

void onMessage(char* topic, byte* payload, unsigned int len) {
  StaticJsonDocument<128> d;
  if (deserializeJson(d, payload, len)) return;
  const char* action = d["action"] | "";
  if (!strcmp(action, "unlock")) {
    int sec = constrain((int)(d["duration"] | 5), 1, 60);
    setLock(true, sec * 1000UL);
  } else if (!strcmp(action, "lock")) {
    setLock(false);
  }
}

void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  unsigned long t = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t < 15000) delay(250);
}

void connectMqtt() {
  if (WiFi.status() != WL_CONNECTED) { connectWifi(); return; }
  String cid = String("esp32-") + DEVICE_ID;
  if (mqtt.connect(cid.c_str())) {
    mqtt.subscribe(topicCmd.c_str(), 1);
    publishStatus();
  }
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(REED_PIN, INPUT_PULLUP);
  relay(false);                       // locked at boot
  topicCmd    = String("smartdoor/") + DEVICE_ID + "/cmd";
  topicStatus = String("smartdoor/") + DEVICE_ID + "/status";
  topicBeat   = String("smartdoor/") + DEVICE_ID + "/heartbeat";
  connectWifi();
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMessage);
}

void loop() {
  if (!mqtt.connected()) {
    if (millis() - lastReconnect > 3000) { lastReconnect = millis(); connectMqtt(); }
  } else {
    mqtt.loop();
  }

  // local auto-relock (works offline)
  if (unlocked && relockAt && (long)(millis() - relockAt) >= 0) setLock(false);

  // door sensor change
  bool doorOpen = digitalRead(REED_PIN) == HIGH;
  if (doorOpen != lastDoorOpen) { lastDoorOpen = doorOpen; if (mqtt.connected()) publishStatus(); }

  if (mqtt.connected() && millis() - lastBeat > 10000) {
    lastBeat = millis();
    StaticJsonDocument<128> d;
    d["state"] = unlocked ? "unlocked" : "locked";
    d["fw"] = FW_VERSION;
    char buf[128];
    serializeJson(d, buf);
    mqtt.publish(topicBeat.c_str(), buf);
  }
}
