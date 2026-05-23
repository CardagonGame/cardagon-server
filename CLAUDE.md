# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup (first time)
uv venv && source .venv/bin/activate && uv sync

# Run dev server (auto-reloads, applies migrations on start)
fastapi dev app/main.py

# Run with Docker (includes Postgres)
docker compose up

# Create a new migration after modifying models.py
alembic revision --autogenerate -m "describe the change"
```

Migrations run automatically on server startup — no manual `alembic upgrade` needed in dev.

## Architecture

**FastAPI + SQLAlchemy + PostgreSQL.** No async ORM — sessions are synchronous (`Session`). WebSockets handle real-time game communication.

### Key layers

- `app/models.py` — All SQLAlchemy ORM models (`User`, `Game`, `GameEvent`, `UserGameAssociation`)
- `app/routers/` — HTTP endpoints (`auth`, `game`, `game_logic`, `user`, `status`, `docs`)
- `app/dependencies/` — FastAPI `Depends()` helpers: `SessionDep` (DB session), `CurrentUserDep` (JWT auth), `game_logic.py` (WebSocket runner + player queries)
- `app/dto/` — Pydantic request/response models. All extend `BaseDTO` from `app/dto/__init__.py`
- `app/game_logic/` — Pure domain logic: `Board`, `Hex`, `Game`, `generate_start_positions`
- `alembic/versions/` — Migration history

### Game event sourcing pattern

Game state is stored as an append-only log of `GameEvent` rows (types: `field_init`, `game_start`, `player_start_position`). `build_game_state()` in `app/dependencies/game_logic.py` replays events to produce the current `GameState`. New game actions append events — never mutate existing rows.

### WebSocket flow

`POST /api/v1/game/join/{join_code}` creates a `UserGameAssociation`. The client then connects to `WS /api/v1/game/{game_id}/ws?token=...`. On connect, the server sends the full `GameState` replay to the new client and broadcasts the updated player list to all. Incoming messages are matched by `type` field (`ping`, `ping_result`, `game_start`).

### Auth

JWT tokens via `OAuth2PasswordBearer`. `CurrentUserDep` (`app/dependencies/user.py`) decodes the token and returns the current user. Registration requires an `INVITE_TOKEN` (set via env var).

### Settings

`app/settings.py` uses `pydantic-settings` — all config comes from environment variables. `DB_CONNECTION_STRING`, `SECRET_KEY`, `INVITE_TOKEN` are the important ones.
