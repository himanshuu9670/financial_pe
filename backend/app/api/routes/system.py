from datetime import datetime, timezone



from fastapi import APIRouter, Depends, Response

from sqlalchemy import func, select, text

from sqlalchemy.orm import Session



from app.api.dependencies import get_db_session

from app.core.config import get_settings

from app.models import ExportJob

from app.monitoring.export_metrics import set_queue_depth

from app.monitoring.health import run_health_checks

from app.monitoring.metrics import prometheus_response

from app.monitoring.redis_metrics import cache_overview, collect_redis_info

from app.monitoring.worker_metrics import inspect_workers

from app.schemas.admin import SystemStatusResponse

from app.services.storage_optimizer import StorageOptimizer



router = APIRouter(tags=["system"])





@router.get("/system-status", response_model=SystemStatusResponse)

def system_status(db: Session = Depends(get_db_session)) -> SystemStatusResponse:

    report = run_health_checks(db)

    queue_depth = db.scalar(

        select(func.count()).select_from(ExportJob).where(ExportJob.status.in_(("queued", "processing")))

    ) or 0

    set_queue_depth(queue_depth)

    storage = StorageOptimizer().disk_usage_summary()



    return SystemStatusResponse(

        status=report["status"],

        database=report["checks"]["database"],

        redis=report["checks"]["redis"],

        celery_workers=report["celery"].get("workers_online", 0),

        storage=storage,

        queue_depth=queue_depth,

        timestamp=datetime.now(timezone.utc),

    )





@router.get("/metrics", response_model=None)

def prometheus_metrics(format: str = "prometheus") -> Response | dict:

    """Prometheus scrape endpoint (default) or JSON operational summary."""

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

    return Response(content=body, media_type=content_type)


