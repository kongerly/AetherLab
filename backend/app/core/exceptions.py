"""Application exception definitions."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard API error response."""

    code: str
    message: str
    request_id: str | None = None


class AetherLabError(Exception):
    """Base exception for AetherLab."""


class ResourceNotFoundError(AetherLabError):
    """Raised when a requested resource does not exist."""
