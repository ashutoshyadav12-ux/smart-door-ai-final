# 🚪 Smart Door AI

Face-recognition smart door lock: **Django REST backend** + **React dashboard** + **ESP32 / MQTT** door controller.

```
smart-door-ai/
├── backend/      Django + DRF + SimpleJWT  (AI pipeline, access control, IoT)
├── frontend/     React + Vite + Tailwind dashboard  → deploy on Vercel
├── esp32/        Arduino firmware + wiring
├── mosquitto/    MQTT broker config
├── docs/         architecture, setup, deployment, api, hardware, security, demo
├── docker-compose.yml   backend + Mosquitto
└── render.yaml          one-click backend deploy on Render
```

## Quick start (local)
```bash
# 1) backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt                         # add -r requirements-ai.txt for real recognition
cp .env.example .env                                    # Windows: copy .env.example .env
#   edit .env -> DEBUG=1, AI_BACKEND=mock (or insightface), ADMIN_PASSWORD=...
python manage.py migrate && python manage.py seed
python manage.py runserver

# 2) frontend (new terminal)
cd frontend
cp .env.example .env                                    # VITE_API_URL=http://localhost:8000
npm install && npm run dev                              # http://localhost:5173
```
Login with `ADMIN_USERNAME` / `ADMIN_PASSWORD` from `backend/.env` (default `admin` / `admin12345` if unset).

## Go live → see [docs/deployment.md](docs/deployment.md)
Frontend → **Vercel**, backend → **Render** (or any Docker host). Vercel cannot run the Django/AI backend (serverless: no long-running threads, no MQTT, size limits), so they are deployed separately.

## Modes
| Setting | Values | Meaning |
|---|---|---|
| `AI_BACKEND` | `mock` / `insightface` | fake embeddings (cloud demo) vs real ArcFace |
| `IOT_MODE` | `demo` / `real` | software door vs MQTT → ESP32 |
