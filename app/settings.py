import tomllib
from pathlib import Path

from pydantic_settings import BaseSettings

_project = tomllib.loads(Path("pyproject.toml").read_text())
PROJECT_NAME: str = _project["project"]["name"]
PROJECT_VERSION: str = _project["project"]["version"]


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
