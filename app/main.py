from fastapi import FastAPI

from app.routers import status, users

app = FastAPI()

app.include_router(status.router)
app.include_router(users.router)
