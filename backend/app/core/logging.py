"""JSON application logging with request context."""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

from app.core.config import settings

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """Serialize approved log fields without exception bodies or arbitrary extras."""

    def format(self, record: logging.LogRecord) -> str:
        """Return a JSON log entry."""
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_context.get(),
        }
        for field in ("method", "route", "status", "latency_ms", "error"):
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    """Configure the application logger without changing third-party handlers."""
    logger = logging.getLogger("app")
    logger.setLevel(settings.log_level)
    logger.propagate = False
    if not any(isinstance(handler.formatter, JsonFormatter) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
