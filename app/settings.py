from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_connection_string: str = "sqlite:///./dev.db"

settings = Settings()