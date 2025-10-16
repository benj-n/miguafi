import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings

from .db import Base, engine
from .routers import auth, users, availability, notifications, dogs


def create_app() -> FastAPI:
	app = FastAPI(title="Miguafi API", version="0.1.0")

	# CORS for local web dev (Vite default port 5173)
	origins = [o.strip() for o in settings.cors_origins.split(',') if o.strip()]
	app.add_middleware(
		CORSMiddleware,
		allow_origins=origins,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	# Basic health
	@app.get("/health")
	def health():
		return {"status": "ok"}

	# DB init - controlled by settings
	if settings.reset_db_on_startup:
		Base.metadata.drop_all(bind=engine)
		Base.metadata.create_all(bind=engine)

	# Static files for local uploads
	if settings.storage_backend == "local":
		os.makedirs(settings.storage_local_dir, exist_ok=True)
		# Serve local uploads under /static/uploads
		uploads_mount = settings.storage_local_dir
		app.mount("/static/uploads", StaticFiles(directory=uploads_mount), name="uploads")

	# Routers
	app.include_router(auth.router, prefix="/auth", tags=["auth"])
	app.include_router(users.router, prefix="/users", tags=["users"])
	app.include_router(availability.router, prefix="/availability", tags=["availability"])
	app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
	app.include_router(dogs.router, prefix="/dogs", tags=["dogs"])

	return app


app = create_app()

