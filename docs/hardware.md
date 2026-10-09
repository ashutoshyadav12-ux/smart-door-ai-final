# Hardware & wiring
- ESP32 dev board, 5V 1-channel **optocoupler** relay module, 12V solenoid/electric strike with its **own** supply,
  1N4007 flyback diode across the coil, reed switch + magnet, LED (220Ω), active buzzer.
- GPIO: relay 26, LED 2, buzzer 27, reed 25 (see `esp32/README.md`).
- Never power the solenoid from the ESP32. Common ground only between ESP32 and relay board.
- Use a fail-secure strike (locked when unpowered) and keep a mechanical key override for power loss/emergency exit.
