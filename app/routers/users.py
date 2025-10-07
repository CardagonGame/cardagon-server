from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.dependencies.db import SessionDep
from app.models.user import User, UserCreate, UserUpdate


router = APIRouter(tags=["users"])


@router.post("/users/")
async def create_user(user_data: UserCreate, session: SessionDep):
    user = User.model_validate(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/users/{user_id}")
async def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/")
async def read_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users


@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = user_data.model_dump(exclude_unset=True)
    for key, value in user_dict.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
