from fastapi import APIRouter
from sqlmodel import select

from app.dependencies.db import SessionDep
from app.models.user import User


router = APIRouter(tags=["users"])


@router.post("/users/")
async def create_user(user: User, session: SessionDep):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/users/{user_id}")
async def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    return user


@router.get("/users/")
async def read_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
    return {"ok": True}
