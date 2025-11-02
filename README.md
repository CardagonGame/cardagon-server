# cardagon-server

cardagon server

## Getting Started

### Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation)

### Setup

Create virtual environment (first time only)

```bash
uv venv
```

Activate virtual environment

```bash
source .venv/bin/activate
```

Install dependencies

```bash
uv sync
```

### Run server

```bash
fastapi dev app/main.py
```

## Database Migrations

After modifying the database models, create a new migration with:

```bash
alembic revision --autogenerate
```

Migrations will be automatically applied on server start.
