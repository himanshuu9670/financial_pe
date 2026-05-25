from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.core.config import get_settings
from app.monitoring.health import run_health_checks
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=None)
def health_check(
    db: Session = Depends(get_db_session),
    detailed: bool = Query(default=False, description="Include full subsystem checks"),
) -> HealthResponse | dict:
    if detailed:
        return run_health_checks(db)

    report = run_health_checks(db)
    settings = get_settings()
    return HealthResponse(
        status=report["status"] if report["status"] != "unhealthy" else "degraded",
        app=settings.app_name,
        database=report["checks"]["database"],
        redis=report["checks"]["redis"],
        timestamp=datetime.now(timezone.utc),
    )
