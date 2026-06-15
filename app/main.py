from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.dependencies.db import check_db_connection, run_migrations
from app.routers import auth, docs, game, game_logic, status, user
from app.settings import PROJECT_NAME, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_db_connection()
    run_migrations()
    yield


app = FastAPI(title=PROJECT_NAME, lifespan=lifespan, docs_url=None, redoc_url=None)
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(docs.router)
app.include_router(game.router)
app.include_router(game_logic.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
