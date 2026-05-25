from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.middleware import register_exception_handlers
from app.api.middleware.rate_limit import limiter
from app.api.middleware.request_timing import RequestTimingMiddleware
from app.api.middleware.security_headers import SecurityHeadersMiddleware
from app.api.routes import api_router
from app.core.config import get_settings
from app.core.observability.sentry_setup import init_sentry
from app.monitoring import setup_monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_storage_dirs()
    yield


def create_app() -> FastAPI:
    setup_monitoring()
    init_sentry()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        description="AI-powered Bank Statement PDF Editor API",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def root():
        return {
            "app": settings.app_name,
            "version": "0.1.0",
            "docs": "/docs",
            "api": settings.api_v1_prefix,
        }

    @app.get("/metrics")
    def root_metrics(format: str = "prometheus"):
        """Root-level prometheus scrape endpoint for legacy integrations/tests."""
        from app.monitoring.metrics import prometheus_response
        from app.monitoring.redis_metrics import collect_redis_info
        from app.services.storage_optimizer import StorageOptimizer
        from app.monitoring.worker_metrics import inspect_workers
        from app.monitoring.redis_metrics import cache_overview
        from app.core.config import get_settings

        # Keep side-effects consistent with system.prometheus_metrics
        collect_redis_info()
        storage = StorageOptimizer().disk_usage_summary()

        if format == "json":
            return {
                "app": get_settings().app_name,
                "env": get_settings().app_env,
                "storage_bytes_total": sum(storage.values()),
                "storage": storage,
                "cache": cache_overview(),
                "celery": inspect_workers(),
            }
        body, content_type = prometheus_response()
        from fastapi import Response

        return Response(content=body, media_type=content_type)

    return app


app = create_app()
