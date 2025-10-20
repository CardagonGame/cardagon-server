from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_CONNECTION_STRING: str = "sqlite:///./dev.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 525600 # 1 year

settings = Settings()