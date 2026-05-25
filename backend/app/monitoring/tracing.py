"""Request correlation IDs and structured log context."""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar

import structlog

from app.core.config import get_settings

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


def bind_request_context(
    *,
    request_id: str | None = None,
    path: str | None = None,
    method: str | None = None,
) -> None:
    rid = request_id or new_request_id()
    request_id_var.set(rid)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=rid,
        path=path,
        method=method,
    )


def clear_request_context() -> None:
    request_id_var.set(None)
    structlog.contextvars.clear_contextvars()


def get_request_id() -> str | None:
    return request_id_var.get()


def configure_structured_logging() -> None:
    """Enhance structlog with request_id processor (idempotent)."""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    def add_request_id(_, __, event_dict):
        rid = request_id_var.get()
        if rid:
            event_dict["request_id"] = rid
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_request_id,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=log_level)
