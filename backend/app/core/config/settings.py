from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Financial PDF Editor"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = (
        "postgresql+psycopg2://pdf_editor:pdf_editor_secret@localhost:5432/pdf_editor_db"
    )

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    storage_root: Path = Path("./storage")
    storage_original: Path = Path("./storage/original_pdfs")
    storage_edited: Path = Path("./storage/edited_pdfs")
    storage_previews: Path = Path("./storage/previews")
    storage_temp: Path = Path("./storage/temp")
    storage_logs: Path = Path("./storage/logs")

    log_level: str = "INFO"
    max_upload_size_mb: int = 50

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def ensure_storage_dirs(self) -> None:
        for path in (
            self.storage_root,
            self.storage_original,
            self.storage_edited,
            self.storage_previews,
            self.storage_temp,
            self.storage_logs,
        ):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_storage_dirs()
    return settings
