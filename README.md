# AetherLab

AetherLab is a modular AI engineering platform for experimenting with and building
LLM inference, RAG, agents, evaluation, and observability workflows.

> **Status:** Pre-Alpha / Phase 0. The project currently provides an initial FastAPI
> backend foundation with tested health checks, configuration, JSON request logs,
> correlated error responses, and a CI workflow. Phase 0 implementation is complete;
> remote CI validation is pending. AI platform capabilities remain planned.

## Available Today

- Python 3.13 backend managed with `uv`
- FastAPI application with OpenAPI documentation
- `GET /health` health check
- Ruff linting and formatting configuration
- Health, configuration, error-contract, and request-context tests
- Validated environment configuration and a backend dotenv template
- JSON application logs and server-generated `X-Request-ID` response headers
- Consistent HTTP, validation, domain, and unexpected-error responses
- GitHub Actions backend checks on relevant pushes and pull requests
- Shared VS Code workspace settings
- Architecture, roadmap, backend, and engineering documentation

## Planned Direction

AetherLab is intended to grow through small, working vertical slices:

1. OpenAI-compatible LLM provider, chat API, SSE streaming, minimal web UI, and tracing
2. Conversation persistence with PostgreSQL
3. Basic RAG with traceable citations and evaluation
4. Tool calling and a bounded agent loop
5. Broader evaluation, observability, and workflow capabilities

## Documentation

- [Project design](docs/design.md): stable product direction, principles, architecture,
  and technology choices
- [Roadmap](docs/roadmap.md): current status, development phases, and completion criteria
- [Backend design](docs/backend.md): layering, providers, Chat, SSE, errors, logging, and
  tracing
- [Engineering guide](docs/engineering.md): workflow, code quality, testing, CI,
  security, and public-repository policy

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

Docker Compose, the frontend, and external model services are not configured yet.

## Quick Start

Install the locked backend dependencies:

```bash
cd backend
uv sync --frozen
```

Defaults work without a dotenv file. For local overrides, copy
`backend/.env.example` to `backend/.env` and set:

| Variable | Default | Allowed values |
| --- | --- | --- |
| `APP_ENV` | `development` | `development`, `test`, `production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

Environment variables override dotenv values. Invalid values fail at startup.
Run commands from `backend/`; the root `.env.example` only points to the backend template.

Start the development server:

```bash
uv run uvicorn app.main:app --reload --no-access-log
```

The service is available at:

- API: <http://127.0.0.1:8000>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "aetherlab"
}
```

Every HTTP response includes a new server-generated `X-Request-ID`. Incoming request
IDs are not reused. Application logs use JSON with the same ID, route template,
status, elapsed milliseconds, and error code. Unknown routes are logged as
`<unmatched>`; raw paths, query strings, request bodies, and exception text are omitted.
Keep `--no-access-log` to prevent Uvicorn's separate access logger from logging raw URLs.
Uvicorn lifecycle logs retain their standard format. `LOG_LEVEL` controls application
logs; levels above `INFO` suppress ordinary request completion logs.

Errors use `{ "code": "...", "message": "...", "request_id": "..." }`, including
404, 405, validation failures, and unexpected failures before response headers are sent.
Error messages are fixed and do not expose input values or exception details.
Streaming lifecycle handling and distributed tracing belong to Phase 1.

## Development Checks

Run these commands from `backend/`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Tests cover health responses, configuration validation, error contracts, request ID
correlation, concurrent context isolation, and sanitized JSON logs. Tests use no model
services or API keys. CI synchronizes dependencies with `uv sync --frozen` before
running the same lint, format, and test checks.

## Repository Structure

```text
AetherLab/
|-- backend/             FastAPI backend and Python project files
|-- frontend/            Future React and TypeScript client
|-- docs/                Project documentation
|   |-- design.md        Stable product and architecture direction
|   |-- roadmap.md       Current status and development phases
|   |-- backend.md       Backend architecture and contracts
|   `-- engineering.md   Repository workflow and quality standards
|-- scripts/             Project automation
|-- data/                Ignored local runtime data
|-- .github/             Repository automation and backend CI
|-- AGENTS.md            Public AI-assisted development guidelines
|-- .env.example         Pointer to backend/.env.example
|-- docker-compose.yml   Reserved; no services needed for Phase 0
`-- README.md
```

## AI-Assisted Development

The committed [AGENTS.md](AGENTS.md) contains public, repository-wide instructions for
AI coding agents. It intentionally contains no credentials, private endpoints, personal
paths, or machine-specific configuration.

For private Codex instructions that apply only to this checkout:

1. Copy `AGENTS.md` to `AGENTS.override.md`.
2. Add the local instructions to that copy.
3. Keep secrets in `.env` or a secret manager, not in either agent instruction file.

`AGENTS.override.md` is ignored by Git. Codex gives it precedence over `AGENTS.md` in
the same directory, so it replaces the repository file rather than merging with it.
Reusable personal defaults that apply across repositories can instead live in
`~/.codex/AGENTS.md`.

See the [official Codex `AGENTS.md` documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
for discovery order, scope, and override behavior.

## Development Principles

- Build small, complete vertical slices.
- Avoid speculative abstractions and empty module scaffolding.
- Add tests alongside new behavior.
- Make LLM operations observable and evaluatable from their first implementation.
- Keep key providers and infrastructure components replaceable.
- Never commit secrets, local data, model files, or populated `.env` files.

## Contributing

The project is in an early stage. Before making changes, read [AGENTS.md](AGENTS.md) and
the relevant document under [`docs/`](docs/). Keep documentation aligned with implemented
behavior and run the relevant checks before opening a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
