# cardagon-server

cardagon server

## Getting Started

### Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation)

#### Setup

```bash
# Create virtual environment (first time only)
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync
```

#### Run server

```bash
fastapi dev app/main.py
```
