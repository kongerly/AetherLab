"""Request correlation and HTTP completion logging."""

import logging
from time import perf_counter
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.exceptions import ErrorResponse
from app.core.logging import request_id_context

logger = logging.getLogger(__name__)


class RequestContextMiddleware:
    """Assign server-generated request IDs and record sanitized HTTP outcomes."""

    def __init__(self, app: ASGIApp) -> None:
        """Wrap the downstream application."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Correlate a request, its response, and its completion log."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid4().hex
        token = request_id_context.set(request_id)
        scope.setdefault("state", {})["request_id"] = request_id
        started = perf_counter()
        status = 500
        response_started = False

        async def send_with_context(message: Message) -> None:
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, send_with_context)
        except Exception:
            scope["state"]["error_code"] = "INTERNAL_SERVER_ERROR"
            if response_started:
                # An already-started response cannot be replaced with a JSON error.
                raise
            response = JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    code="INTERNAL_SERVER_ERROR",
                    message="Internal server error",
                    request_id=request_id,
                ).model_dump(),
            )
            await response(scope, receive, send_with_context)
        finally:
            try:
                route = scope.get("route")
                error = scope["state"].get("error_code")
                logger.log(
                    logging.ERROR
                    if status >= 500 or error == "INTERNAL_SERVER_ERROR"
                    else logging.INFO,
                    "HTTP request completed",
                    extra={
                        "method": scope["method"],
                        "route": getattr(route, "path", "<unmatched>"),
                        "status": status,
                        "latency_ms": round((perf_counter() - started) * 1000, 3),
                        "error": error,
                    },
                )
            finally:
                request_id_context.reset(token)
