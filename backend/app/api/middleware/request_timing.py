"""Request timing, tracing, and API metrics middleware."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.monitoring.api_metrics import record_request
from app.monitoring.tracing import bind_request_context, clear_request_context, get_request_id


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        return route.path
    return request.url.path.split("?")[0][:80]


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        bind_request_context(
            request_id=request.headers.get("X-Request-ID"),
            path=request.url.path,
            method=request.method,
        )
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration = time.perf_counter() - start
            path = request.url.path
            if "/metrics" not in path and not path.endswith("/health"):
                record_request(request.method, _route_template(request), 500, duration)
            clear_request_context()
            raise

        duration = time.perf_counter() - start
        path = request.url.path
        if "/metrics" not in path and not path.endswith("/health"):
            record_request(
                request.method,
                _route_template(request),
                response.status_code,
                duration,
            )
        rid = get_request_id()
        if rid:
            response.headers["X-Request-ID"] = rid
        response.headers["X-Response-Time-Ms"] = f"{duration * 1000:.1f}"
        clear_request_context()
        return response
