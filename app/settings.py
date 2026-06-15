import os
import tomllib
from pathlib import Path

from pydantic_settings import BaseSettings

try:
    _pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    _project = tomllib.loads(_pyproject_path.read_text())["project"]
    PROJECT_NAME: str = _project["name"]
    PROJECT_VERSION: str = _project["version"]
except (FileNotFoundError, tomllib.TOMLDecodeError, KeyError):
    PROJECT_NAME = os.getenv("PROJECT_NAME", "unknown")
    PROJECT_VERSION = os.getenv("PROJECT_VERSION", "unknown")


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str = (
        "postgresql://cardagon:5RcBPgUL2IbKYGuE@localhost:5432/cardagondb"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600  # 1 year
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    INVITE_TOKEN: str = "DEV_INVITE_TOKEN"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
