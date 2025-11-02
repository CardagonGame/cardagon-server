import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.dependencies.db import SessionDep
from app.dependencies.security import (
    get_password_hash,
    oauth2_password,
    verify_password,
)
from app.dto.user import UserCreate, UserPublic
from app.models import User
from app.settings import settings

TokenDep = Annotated[str, Depends(oauth2_password)]


def user_authenticate(*, session: Session, username: str, password: str) -> User | None:
    db_user = get_user_by_username(session=session, username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    return db_user


def get_user_by_username(*, session: Session, username: str) -> User | None:
    session_user = session.query(User).filter(User.username == username).first()
    return session_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    session_user = session.query(User).filter(User.email == email).first()
    return session_user


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User(
        email=user_create.email,
        username=user_create.username,
        password_hash=get_password_hash(user_create.password),
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return UserPublic(
        id=str(db_obj.id),
        email=db_obj.email,
        username=db_obj.username,
    )


def get_current_user(
    session: SessionDep, token: str = Depends(oauth2_password)
) -> UserPublic:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic(email=user.email, username=user.username, id=str(user.id))


CurrentUserDep = Annotated[UserPublic, Depends(get_current_user)]
