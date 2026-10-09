# ESP32 firmware

## Pinout
| ESP32 pin | Connects to |
|---|---|
| GPIO26 | Relay module IN |
| GPIO2 | Status LED (+ 220Ω to GND) |
| GPIO27 | Active buzzer |
| GPIO25 | Magnetic reed sensor → other leg to GND |
| 5V / GND | Relay VCC / GND |

Relay COM/NO switch the **separate** 12V supply to the solenoid lock. Put a 1N4007 flyback diode across the solenoid.

## Flash
1. Arduino IDE → install *ESP32 board package*, libraries **PubSubClient** and **ArduinoJson 6.x**.
2. Edit Wi-Fi, `MQTT_HOST` (your server IP) and `DEVICE_ID` at the top of `smart_door.ino`.
3. Board: *ESP32 Dev Module* → Upload.
4. Backend `.env`: `IOT_MODE=real`, `MQTT_HOST=<broker>`, `MQTT_DEVICE_ID=door01`.

The board always boots **locked** and relocks itself locally even if Wi-Fi/MQTT drops.
