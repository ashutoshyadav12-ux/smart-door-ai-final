# REST API
See the endpoint table in `backend/README.md`. All routes are under `/api`, JWT bearer auth
(`POST /api/auth/login` → `access`). Public: `/api/health`, `/api/auth/login`, `/api/iot/heartbeat` (device key).
Pagination: `?page=N` on users and access-logs (`count/next/previous/results`).
