"""Optional Sentry initialization — no-op when DSN unset."""

from __future__ import annotations

from app.core.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


def init_sentry() -> None:
    settings = get_settings()
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            integrations=[
                FastApiIntegration(),
                CeleryIntegration(),
                SqlalchemyIntegration(),
            ],
            send_default_pii=False,
        )
        logger.info("sentry_initialized", env=settings.app_env)
    except ImportError:
        logger.warning("sentry_sdk_not_installed")
    except Exception as exc:
        logger.warning("sentry_init_failed", error=str(exc))
