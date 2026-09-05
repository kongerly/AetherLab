"""Health check routes."""

from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get("")
async def health() -> dict[str, str]:
    """Return the current health status of the backend service."""
    return {
        "status": "ok",
        "service": "aetherlab",
    }
