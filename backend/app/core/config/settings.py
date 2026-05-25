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

    # Auth (Phase 8)
    auth_disabled: bool = True
    jwt_secret_key: str = "change-me-jwt-secret-min-32-chars-long"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    secure_download_expire_minutes: int = 15

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_default: str = "120/minute"
    rate_limit_upload: str = "20/hour"
    rate_limit_auth: str = "30/minute"
    rate_limit_export: str = "40/hour"

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
    storage_snapshots: Path = Path("./storage/snapshots")
    storage_exports: Path = Path("./storage/exports")
    storage_previews: Path = Path("./storage/previews")
    storage_temp: Path = Path("./storage/temp")
    storage_logs: Path = Path("./storage/logs")
    temp_retention_hours: int = 24
    export_retention_days: int = 90

    log_level: str = "INFO"
    max_upload_size_mb: int = 50

    # Phase 9 — AI intelligence
    ai_embeddings_dim: int = 64
    ai_cache_embeddings: bool = True
    ai_auto_analyze_after_parse: bool = True

    # Phase 10 — performance & deployment
    redis_cache_enabled: bool = True
    cache_ttl_extraction: int = 3600
    cache_ttl_ocr: int = 86400
    cache_ttl_ai: int = 1800
    cache_ttl_transactions: int = 3600
    cache_ttl_preview: int = 300
    pdf_page_batch_size: int = 25
    pdf_max_pages_in_memory: int = 500
    rate_limit_ocr: str = "30/hour"
    rate_limit_ai: str = "60/hour"
    rate_limit_extract: str = "120/hour"
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1
    prometheus_enabled: bool = True
    storage_backend: str = "local"  # local | s3
    s3_bucket: str = ""
    s3_prefix: str = "statements"
    s3_region: str = "us-east-1"
    s3_endpoint_url: str = ""
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

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
            self.storage_snapshots,
            self.storage_exports,
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
