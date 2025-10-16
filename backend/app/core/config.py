from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Miguafi API"
    secret_key: str = Field("dev-secret", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field("sqlite:///./miguafi.db", env="DATABASE_URL")
    cors_origins: str = Field("http://localhost:5173,http://127.0.0.1:5173", env="CORS_ORIGINS")
    app_env: str = Field("dev", env="APP_ENV")
    reset_db_on_startup: bool = Field(True, env="RESET_DB_ON_STARTUP")
    # Storage
    storage_backend: str = Field("local", env="STORAGE_BACKEND")  # local | s3
    storage_local_dir: str = Field("./uploads", env="STORAGE_LOCAL_DIR")
    s3_endpoint_url: str | None = Field(None, env="S3_ENDPOINT_URL")
    s3_access_key: str | None = Field(None, env="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(None, env="S3_SECRET_KEY")
    s3_region: str | None = Field(None, env="S3_REGION")
    s3_bucket: str | None = Field(None, env="S3_BUCKET")
    # Optional public base URL (e.g., http://localhost:9000/<bucket>) to construct browser-friendly URLs
    s3_public_base_url: str | None = Field(None, env="S3_PUBLIC_BASE_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def reload_settings() -> None:
    get_settings.cache_clear()  # type: ignore[attr-defined]
    global settings
    settings = get_settings()
