# Local setup (Windows)
1. Install Python 3.11+, Node 18+, Git.
2. Backend: `cd backend`, `python -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`
   (real AI: also `pip install -r requirements-ai.txt`; needs Microsoft C++ Build Tools for insightface).
3. `copy .env.example .env` → set `DEBUG=1`, `AI_BACKEND=mock|insightface`.
4. `python manage.py migrate` → `python manage.py seed` → `python manage.py runserver`.
5. Frontend: `cd frontend`, `copy .env.example .env`, `npm install`, `npm run dev`.
6. MQTT (optional): `docker compose up mosquitto`.
7. Tests: `python manage.py test door`.
