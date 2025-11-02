from typing import Annotated

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext

from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.settings import settings

engine = create_engine(settings.DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "./alembic")
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied successfully")


def check_db_connection():
    try:
        with Session(engine) as session:
            session.execute(select(1))
    except Exception as e:
        print("Database connection failed:", e)
        raise e
    print("DB connection successful")
