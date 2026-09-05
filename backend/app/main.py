"""AetherLab backend application entry point."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.routes.health import health_router
from app.core.exceptions import ErrorResponse, ResourceNotFoundError
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="AetherLab", version="0.1.0")
logger.info("AetherLab backend initialized")
app.include_router(health_router)
app.add_middleware(RequestContextMiddleware)


def error_response(
    request: Request,
    status: int,
    code: str,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Build a correlated error response using safe, fixed messages."""
    request.state.error_code = code
    return JSONResponse(
        status_code=status,
        content=ErrorResponse(
            code=code, message=message, request_id=request.state.request_id
        ).model_dump(),
        headers=headers,
    )


@app.exception_handler(ResourceNotFoundError)
async def handle_resource_not_found(request: Request, _exc: ResourceNotFoundError) -> JSONResponse:
    """Convert resource-not-found errors into HTTP responses."""
    return error_response(request, 404, "RESOURCE_NOT_FOUND", "Resource not found")


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    """Normalize framework HTTP errors while preserving protocol headers."""
    try:
        status = HTTPStatus(exc.status_code)
        code, message = status.name, status.phrase
    except ValueError:
        code, message = "HTTP_ERROR", "HTTP request failed"
    return error_response(request, exc.status_code, code, message, exc.headers)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, _exc: RequestValidationError) -> JSONResponse:
    """Report invalid input without echoing user data."""
    return error_response(request, 422, "VALIDATION_ERROR", "Request validation failed")
