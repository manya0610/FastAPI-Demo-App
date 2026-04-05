# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run application (development)
. .env && uvicorn src.app:app --host 0.0.0.0 --port 8000

# Run tests with coverage
make test
# Or manually: . .env.test.rc && python3 -m pytest --cov=src -s

# Run a single test file
. .env.test.rc && python3 -m pytest tests/service/test_user_service.py -s

# Run a single test by name
. .env.test.rc && python3 -m pytest -k "test_name" -s

# Lint and format
make lint
make format

# Database setup (create DB, run migrations, seed data)
make db_setup

# Run Alembic migrations
make create_tables

# Generate HTML coverage report
make test-coverage
```

## Architecture

Layered architecture with clear separation: **Router → Service → Repository → Database**

```
src/
├── app/            # FastAPI app + routers (auth_router, user_router, deps)
├── services/       # Business logic (UserService) — caching, validation, auth
├── repo/postgres/  # Data access (BaseRepository[T], UserRepository, UnitOfWork)
├── database/       # SQLAlchemy async engine, session factory, ORM models
├── auth/           # JWT creation/validation, Argon2ID password hashing
├── schemas/        # Pydantic DTOs (UserCreate, UserPublic, UserUpdate)
├── redis_client.py # Singleton RedisClient + MockRedisClient for tests
├── rmq/            # RabbitMQ publisher + worker for async user registration
└── exceptions/     # Custom exception hierarchy (db_exceptions, request_exceptions)
```

### Key Patterns

**Repository + UnitOfWork**: `BaseRepository[T]` provides generic async CRUD. `UnitOfWork` (in `db_helper.py`) wraps sessions in an async context manager for transaction control. Services receive a `UnitOfWork` instance via FastAPI `Depends()`.

**Caching**: `UserService` implements Redis (1-hour TTL) → PostgreSQL fallback. Cache is invalidated on updates. If Redis is unavailable, falls back silently to DB. Cache key format: `user:{id}`.

**Async user registration**: `POST /user/register-async` publishes to RabbitMQ; the worker in `rmq/worker.py` consumes messages and persists to DB.

**Dependency injection**: All services and repos are wired in `app/routers/deps.py` using `Depends()`.

### Environment Files

- `.env` — local development
- `.env.test.rc` — test environment (separate test DB, must be sourced before running tests)
- `.env.docker.rc` — Docker (uses `host.docker.internal`)

Key env vars: `DATABASE_URL`, `REDIS_URL`, `REDIS_DATABASE_INDEX`, `RMQ_BROKER_URL`, `RMQ_QUEUE`, `RMQ_EXCHANGE`

### Testing

Tests use a real test database (not mocked). `MockRedisClient` is used for Redis. Fixtures in `tests/conftest.py` auto-create/drop tables per session and truncate between tests. All tests are async (`pytest-asyncio`).
