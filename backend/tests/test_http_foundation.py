"""Behavioral checks for error contracts and request logging."""

import asyncio
import io
import json
import logging
from collections.abc import Iterator
from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

from app.core.exceptions import ResourceNotFoundError
from app.core.logging import JsonFormatter, configure_logging, request_id_context
from app.core.middleware import RequestContextMiddleware
from app.main import app


@pytest.fixture
def log_output() -> Iterator[io.StringIO]:
    """Capture the actual JSON formatter output."""
    output = io.StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        yield output
    finally:
        logger.removeHandler(handler)


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Use production error handlers with test-only failure routes."""
    test_app = FastAPI(exception_handlers=app.exception_handlers)
    test_app.add_middleware(RequestContextMiddleware)

    @test_app.get("/items/{item_id}")
    async def item(item_id: int) -> dict[str, int]:
        return {"id": item_id}

    @test_app.get("/missing")
    async def missing() -> None:
        raise ResourceNotFoundError("secret-exception-body")

    @test_app.get("/broken")
    async def broken() -> None:
        raise RuntimeError("secret-exception-body")

    @test_app.get("/unauthorized")
    async def unauthorized() -> None:
        raise HTTPException(401, "secret-exception-body", headers={"WWW-Authenticate": "Bearer"})

    with TestClient(test_app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("method", "path", "status", "code", "message"),
    [
        ("GET", "/secret-path", 404, "NOT_FOUND", "Not Found"),
        ("POST", "/items/1", 405, "METHOD_NOT_ALLOWED", "Method Not Allowed"),
        ("GET", "/items/secret-input", 422, "VALIDATION_ERROR", "Request validation failed"),
        ("GET", "/missing", 404, "RESOURCE_NOT_FOUND", "Resource not found"),
        ("GET", "/broken", 500, "INTERNAL_SERVER_ERROR", "Internal server error"),
        ("GET", "/unauthorized", 401, "UNAUTHORIZED", "Unauthorized"),
    ],
)
def test_errors(
    client: TestClient,
    log_output: io.StringIO,
    method: str,
    path: str,
    status: int,
    code: str,
    message: str,
) -> None:
    """Return safe correlated errors and log exactly one sanitized outcome."""
    response = client.request(
        method,
        path + "?token=secret-query",
        headers={"Authorization": "Bearer secret-header", "X-Request-ID": "secret-client-id"},
    )
    request_id = response.headers["x-request-id"]
    assert UUID(request_id).version == 4
    assert response.status_code == status
    assert response.json() == {"code": code, "message": message, "request_id": request_id}
    if status == 405:
        assert "GET" in response.headers["allow"]
    if status == 401:
        assert response.headers["www-authenticate"] == "Bearer"
    entries = [json.loads(line) for line in log_output.getvalue().splitlines()]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["request_id"] == request_id
    assert entry["status"] == status
    assert entry["error"] == code
    assert entry["latency_ms"] >= 0
    assert entry["level"] == ("ERROR" if status == 500 else "INFO")
    assert "secret-" not in log_output.getvalue() + response.text
    assert request_id_context.get() is None


def test_health_correlation(log_output: io.StringIO) -> None:
    """Generate fresh IDs and preserve the existing health response."""
    with TestClient(app) as client:
        first = client.get("/health")
        second = client.get("/health")
    assert first.json() == {"status": "ok", "service": "aetherlab"}
    assert first.headers["x-request-id"] != second.headers["x-request-id"]
    entries = [json.loads(line) for line in log_output.getvalue().splitlines()]
    assert [entry["request_id"] for entry in entries] == [
        first.headers["x-request-id"],
        second.headers["x-request-id"],
    ]
    assert all(entry["route"] == "/health" and entry["error"] is None for entry in entries)


def test_concurrent_context_isolation(log_output: io.StringIO) -> None:
    """Keep request IDs isolated across overlapping asynchronous requests."""

    async def run() -> None:
        arrived = 0
        ready = asyncio.Event()
        ids = []

        async def endpoint(scope: Scope, receive: Receive, send: Send) -> None:
            nonlocal arrived
            before = request_id_context.get()
            arrived += 1
            if arrived == 2:
                ready.set()
            await asyncio.wait_for(ready.wait(), timeout=2)
            assert request_id_context.get() == before
            ids.append(before)
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        async def receive() -> Message:
            return {"type": "http.request", "body": b""}

        async def send(message: Message) -> None:
            pass

        middleware = RequestContextMiddleware(endpoint)
        await asyncio.gather(
            *(middleware({"type": "http", "method": "GET"}, receive, send) for _ in range(2))
        )
        assert len(set(ids)) == 2
        assert request_id_context.get() is None

    asyncio.run(run())


def test_logging_configuration_is_idempotent() -> None:
    """Avoid duplicate output when application logging is configured again."""
    logger = logging.getLogger("app")
    original = list(logger.handlers)
    configure_logging()
    configure_logging()
    assert logger.handlers == original
