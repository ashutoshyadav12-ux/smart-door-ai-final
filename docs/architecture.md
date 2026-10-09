# Architecture

```
Browser (React) ──REST/JWT──▶ Django API ──▶ FacePipeline (detect → quality → ArcFace 512-d)
      │ webcam frames                      │         │
      └────────────────────────────────────┘         ▼
                                           VectorCache (cosine search)
                                                   ▼
                                           AccessController (liveness, threshold,
                                           cooldown, lockout, logging)
                                                   ▼
                              IOT_MODE=demo → DemoController (timer relock)
                              IOT_MODE=real → MQTT (Mosquitto) → ESP32 → relay/solenoid
```

**Recognition sequence:** frame(s) → `/api/faces/recognize` → decode → detect largest face → quality gate
(sharpness, brightness, size) → optional liveness over 3 frames → embedding → cosine vs cache →
threshold → cooldown/lockout → unlock command → `AccessLog` row.

**Fail-secure:** every error path returns "denied"; ESP32 boots locked and relocks locally.
