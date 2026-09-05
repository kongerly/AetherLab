"""AetherLab backend application entry point."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.health import health_router
from app.core.exceptions import ErrorResponse, ResourceNotFoundError
from app.core.logging import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AetherLab",
    version="0.1.0",
)

logger.info("AetherLab backend initialized")

app.include_router(health_router)


@app.exception_handler(ResourceNotFoundError)
async def handle_resource_not_found(
    _request: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    """Convert resource-not-found errors into HTTP responses."""
    error = ErrorResponse(
        code="RESOURCE_NOT_FOUND",
        message=str(exc),
    )

    return JSONResponse(
        status_code=404,
        content=error.model_dump(),
    )
