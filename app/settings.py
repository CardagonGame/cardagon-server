import secrets

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str = "sqlite:///./dev.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600  # 1 year
    SECRET_KEY: str = "REPLACE_ME_WITH_A_RANDOM_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    INVITE_TOKEN: str = "DEV_INVITE_TOKEN"


settings = Settings()
