# miguafi

Full-stack app scaffold with FastAPI backend and Vite React frontend.

Highlights:
- FastAPI API: auth, users, availability offers/requests with matching, notifications
- Dogs: shared ownership CRUD and photo uploads (local or S3/MinIO)
- Postgres + Alembic migrations
- MailHog for email in dev
- Docker Compose for local dev (db, api, web, mailhog, minio)

Storage backends:
- Local (default): files saved under backend uploads volume and served at /static/uploads/... URLs
- S3/MinIO: set environment STORAGE_BACKEND=s3 and S3_* variables; MinIO service is included and bucket auto-created
