import tomllib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.dependencies.db import check_db_connection, run_migrations
from app.routers import auth, docs, game, status, user

with open("pyproject.toml", "rb") as project_file:
    project_dict = tomllib.load(project_file)
    project_name = project_dict["project"]["name"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_db_connection()
    run_migrations()
    yield


app = FastAPI(title=project_name, lifespan=lifespan, docs_url=None, redoc_url=None)

app.include_router(status.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(docs.router)
app.include_router(game.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
