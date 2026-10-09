# Deployment: GitHub → Render (backend) → Vercel (frontend)

> Why two hosts? Vercel serves static sites/serverless functions. The backend needs a long-running
> process (door state timers, lockout counters, MQTT client, in-memory face cache) so it runs on Render/Railway/VPS.
> Order matters: deploy backend first, then frontend, then fix CORS.

## 1. Push to GitHub
```bash
cd smart-door-ai
git init && git add . && git commit -m "Smart Door AI"
git branch -M main
git remote add origin https://github.com/<you>/smart-door-ai.git
git push -u origin main
```
`.env` files are git-ignored — never commit secrets.

## 2. Backend on Render
1. render.com → **New → Blueprint** → select your repo (uses `render.yaml`).
2. Fill the prompted env vars:
   - `ADMIN_PASSWORD` – your dashboard password
   - `CORS_ORIGINS` – leave blank for now (Vercel URL comes later); `CORS_ALLOW_VERCEL=1` already allows `*.vercel.app`
   - `CSRF_TRUSTED_ORIGINS` – `https://<your-service>.onrender.com`
3. Deploy. Test: `https://<your-service>.onrender.com/api/health` → `{"status":"ok"...}`.

Notes
- Free plan sleeps after inactivity (first request ~30-60s) and its disk is wiped on redeploy → SQLite data (users, face samples) resets.
  For persistence create a free Postgres (Render/Neon/Supabase) and set `DATABASE_URL`.
- Free RAM (512 MB) is too small for InsightFace → keep `AI_BACKEND=mock` for the online demo.
  Real recognition: run `docker compose up --build` with `INSTALL_AI: "1"` on a PC/VPS with ≥2 GB RAM.
- Keep gunicorn at **1 worker** (already set) because state is in memory.

## 3. Frontend on Vercel
1. vercel.com → **Add New → Project** → import the GitHub repo.
2. **Root Directory: `frontend`** (Framework: Vite is auto-detected).
3. Environment Variable: `VITE_API_URL` = `https://<your-service>.onrender.com` (no `/api`, no trailing slash).
4. Deploy → open the URL → log in.
5. Back on Render, set `CORS_ORIGINS=https://<your-project>.vercel.app` (custom domain too) → redeploy.

Browser webcam needs HTTPS — Vercel provides it, so enrollment & live recognition work from the browser camera.

## 4. Real door (ESP32)
Cloud demo uses the virtual door (`IOT_MODE=demo`). For hardware run the backend + Mosquitto on your LAN
(`docker compose up`), set `IOT_MODE=real`, flash `esp32/smart_door.ino`. See `esp32/README.md`.

## Troubleshooting
| Symptom | Fix |
|---|---|
| Login says "Cannot reach backend" | wrong `VITE_API_URL` or CORS_ORIGINS missing your Vercel URL |
| Blank page on refresh at /users | `frontend/vercel.json` rewrite must exist (it does) |
| Camera not starting | needs HTTPS or localhost + browser permission |
| Mixed-content error | backend URL must be `https://` |
