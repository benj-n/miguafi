# Miguafi

Full‑stack app with FastAPI (backend) and Vite + React (web). Features include:
- Auth, user profile, offers/requests with matching and notifications
- Dogs: shared ownership CRUD and photo uploads (local or S3/MinIO)
- Postgres + Alembic migrations (SQLite used by default locally)
- MailHog for local email testing; MinIO for S3‑compatible storage

This README focuses on testing locally (with and without Docker).

## Prerequisites

- Node.js 20.x and npm
- Python 3.12 with pip
- Docker (optional, for full stack with Postgres/MailHog/MinIO)

## Quick start: run tests locally (no Docker)

### Backend tests (pytest)

From repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Run all backend tests
pytest backend/tests -q
```

Notes:
- Default DB is SQLite file at `backend/miguafi.db` (configured via `DATABASE_URL` in settings).
- App setting `RESET_DB_ON_STARTUP=true` resets schema on each app start in dev; tests use TestClient and their own app instance.

Run the API locally for manual checks:

```bash
# in one shell
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --reload --port 8000

# in another shell: smoke test
curl -s http://localhost:8000/health
```

### Web tests (Vitest)

From `web/`:

```bash
cd web
npm ci || npm i

# Run unit tests
npm run test:run
```

Run the web app locally:

```bash
# ensure API is on http://localhost:8000 (see backend run above)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
# open http://localhost:5173
```

## Full stack via Docker Compose

The `infra/docker-compose.yml` provides:
- Postgres (5432)
- MailHog (SMTP 1025, UI 8025)
- API (8000)
- Web (5173) and a web-dev service
- MinIO (S3 API 9000, Console 9001)

Start services:

```bash
cd infra
docker compose up -d --build
# API: http://localhost:8000
# Web: http://localhost:5173
# MailHog UI: http://localhost:8025
# MinIO Console: http://localhost:9001 (user/pass from env or defaults)
```

Environment:
- Copy `.env.example` to `.env` at the repo root and adjust if needed.
- Storage:
	- S3/MinIO (default in docker-compose): API uses MinIO; photos return URLs like `http://localhost:9000/<bucket>/dogs/...`. Configure with `S3_PUBLIC_BASE_URL` for browser-friendly URLs.
	- Local: set `STORAGE_BACKEND=local` to serve under `/static/uploads/...`.

## Database migrations (Alembic)

Alembic is set up under `backend/alembic`. Typical flow:

```bash
cd backend
# point DATABASE_URL to your target (e.g., sqlite or postgres)
export DATABASE_URL=sqlite:///./miguafi.db

# Generate migration from models
alembic -c alembic.ini revision --autogenerate -m "your message"

# Apply migrations
alembic -c alembic.ini upgrade head
```

## API usage examples

Health check:

```bash
curl -s http://localhost:8000/health
```

Register and login to get a token:

```bash
curl -sX POST http://localhost:8000/auth/register \
	-H 'Content-Type: application/json' \
	-d '{"email":"alice@example.com","password":"password123","dog_name":"REX21"}'

TOKEN=$(curl -sX POST http://localhost:8000/auth/login \
	-d 'username=alice@example.com&password=password123' | jq -r .access_token)
echo "Token: $TOKEN"
```

Create a dog (names must be uppercase and end with two digits, e.g., REX21):

```bash
curl -sX POST http://localhost:8000/dogs/ \
	-H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
	-d '{"name":"REX21"}'
```

Upload dog photo (S3/MinIO will return http://localhost:9000/… if S3_PUBLIC_BASE_URL is set):

```bash
curl -sX POST http://localhost:8000/dogs/1/photo \
	-H "Authorization: Bearer $TOKEN" \
	-F 'file=@/path/to/photo.png'
```

## Storage notes

- Local storage: files saved to `STORAGE_LOCAL_DIR` and exposed at `/static/uploads/...` while the API is running.
- S3/MinIO storage: uploads go to the configured bucket; URLs will use `S3_PUBLIC_BASE_URL` when set (e.g., `http://localhost:9000/<bucket>/dogs/...`), else the internal endpoint.
- The web UI enforces client-side checks: `image/*` MIME and max ~5MB. The API also checks `image/*` MIME.

## CI

GitHub Actions workflow `.github/workflows/ci.yml` runs both suites on push/PR to `main`:
- Backend (pytest): `pytest -q backend`
- Web (Vitest): `npm run test:run` in `web/`

## Troubleshooting

- If vite dev can’t reach the API, verify `web/.env.local` has `VITE_API_BASE_URL=http://localhost:8000` and the backend is running.
- For MinIO access, use the console at http://localhost:9001 and check credentials from your env.
- For emails, use MailHog UI at http://localhost:8025.
