# Smart Door AI — Django backend

Django 5 + Django REST Framework + SimpleJWT. Mirrors the planned architecture:
InsightFace pipeline → access controller → demo/MQTT door controller.

## Run (Windows PowerShell shown; same on Linux/macOS)
```
cd backend
python -m venv .venv ; .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed            # admin / admin12345 + demo device
python manage.py runserver 0.0.0.0:8000
```
No GPU / models yet? Set `AI_BACKEND=mock` in `.env` (deterministic fake embeddings).
Tests: `python manage.py test door`

## Endpoints (all JWT-protected except health, login, heartbeat)
| Method | Path | Purpose |
|---|---|---|
| POST | /api/auth/login, /api/auth/refresh | JWT |
| GET | /api/auth/me | current admin |
| CRUD | /api/users | people allowed through the door |
| POST | /api/faces/enroll | multipart `person_id` + `image` (repeat for 5 samples) |
| POST | /api/faces/recognize | multipart `image` (send 3+ frames if liveness on) |
| DELETE | /api/faces/{person_id} | remove all face samples |
| GET | /api/door/status · POST /api/door/unlock · POST /api/door/lock | |
| GET | /api/camera/status · /api/camera/stream?token=JWT | MJPEG |
| GET | /api/access-logs?event_type=&q=&person=&date_from=&date_to= | paginated |
| GET | /api/iot/devices · POST /api/iot/command · POST /api/iot/heartbeat | heartbeat needs `X-Device-Key` |
| GET/PUT | /api/settings | threshold, unlock_duration, liveness_required, lockout… |
| GET | /api/dashboard/stats | dashboard cards + recent events |

## MQTT contract (IOT_MODE=real)
- Backend → ESP32: `smartdoor/<device>/cmd` `{"action":"unlock","duration":5}` / `{"action":"lock"}`
- ESP32 → backend: `smartdoor/<device>/status` and `/heartbeat`, JSON `{"state":"locked|unlocked","fw":"1.0"}`

## Security notes
- Fail-secure: any error, low quality, unknown face, lockout → door stays locked.
- Liveness is a prototype (blink/motion); do not rely on it against video replay.
- Change SECRET_KEY, admin password, DEVICE_API_KEY before any real deployment.
