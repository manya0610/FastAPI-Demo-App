# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make test        # Run all tests (loads .env.test.rc automatically)
make lint        # Run ruff linter
make format      # Fix import order and format code with ruff

# Run a single test file
. .env.test.rc; python3 -m pytest -s tests/service/test_user_service.py

# Run a single test by name
. .env.test.rc; python3 -m pytest -s -k "test_name"

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Architecture

Layered design: **Routers → Services → Repositories → DB / Cache**

### Request Flow

```
HTTP Request
  → Router (src/app/routers/)
  → Dependency Injection (deps.py) — injects UserService, auth via JWT
  → Service (src/services/user_service.py) — business logic + cache-aside
  → Repository (src/repo/postgres/) — DB access via SQLAlchemy async
  → PostgreSQL (via asyncpg) + Redis (cache)
```

### Cache-Aside Pattern (UserService)

All reads check Redis first, fall back to DB, then populate cache. Writes update DB and invalidate/re-cache. **Redis failures are non-fatal** — the service degrades gracefully to DB-only.

Cache keys follow the pattern `user:{id}`, with 3600s TTL.

### Async User Registration via RabbitMQ

`POST /user/register-async` returns 202 immediately after publishing to `user_registration_queue`. The worker (`src/rmq/worker.py`) consumes and calls `UserService.register_user()` in the background.

### Repository Pattern

`BaseRepository[ModelType]` (base_repo.py) is a generic async CRUD base. `UserRepository` extends it with `get_by_username()` for auth. All DB operations use SQLAlchemy async sessions injected via `deps.py`.

### Authentication

JWT-based (HS256). `POST /auth/login` returns a bearer token. Protected routes use the `auth_required` dependency which decodes the token and stores the user in `request.state.user`. Passwords use Argon2ID via `pwdlib`.

## Environment

- `.env` — development
- `.env.test.rc` — test (sourced automatically by `make test`)
- `.env.docker.rc` — Docker

Key vars: `DATABASE_URL`, `REDIS_URL`, `RMQ_BROKER_URL`

## Testing

Tests use a real PostgreSQL database (not mocks). Each test gets a clean state via table truncation after each test (session-scoped DB setup, function-scoped truncation).

`MockRedisWrapper` (in `src/redis_client.py`) is used instead of a real Redis in tests. A `failing_redis` fixture simulates Redis outages to test graceful degradation.

Async tests require `@pytest.mark.asyncio(loop_scope="session")`.
