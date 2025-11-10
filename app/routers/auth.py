from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import security

from app.dependencies.db import SessionDep
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import create_user, get_user_by_email, user_authenticate
from app.dto.user import Token, UserCreate, UserPublic, UserRegister
from app.settings import settings


router = APIRouter(tags=["auth"])


@router.post(f"{API_V1_PREFIX}/register")
def register_user(session: SessionDep, user_in: UserRegister) -> UserPublic:
    if user_in.invite_token != settings.INVITE_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid invite code")
    user = get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="This email address is already registered",
        )
    user_create = UserCreate.model_validate(
        {
            "email": user_in.email,
            "username": user_in.username,
            "password": user_in.password,
            "is_active": True,
            "is_admin": False,
        }
    )
    user = create_user(session=session, user_create=user_create)
    return user


@router.post(f"{API_V1_PREFIX}/login")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return Token(access_token=security.create_access_token(user=user))
