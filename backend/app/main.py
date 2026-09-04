"""AetherLab backend application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="AetherLab",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Return the current health status of the backend service."""
    return {
        "status": "ok",
        "service": "aetherlab",
    }
