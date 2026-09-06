"""携带请求上下文的 JSON 应用日志。"""

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

from app.core.config import settings

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """仅序列化允许的日志字段，排除异常详情和任意附加字段。"""

    def format(self, record: logging.LogRecord) -> str:
        """返回 JSON 格式的日志记录。"""
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
    """配置应用日志记录器，保留第三方日志处理器的配置。"""
    logger = logging.getLogger("app")
    logger.setLevel(settings.log_level)
    logger.propagate = False
    if not any(isinstance(handler.formatter, JsonFormatter) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
