from datetime import datetime, timedelta
from typing import Annotated

from app.dependencies.static import API_V1_PREFIX
import jwt

from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from passlib.context import CryptContext

from app.models import User

from app.settings import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_password = OAuth2PasswordBearer(tokenUrl=f"{API_V1_PREFIX}/login")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(*, user: User):
    encode = {
        "sub": user.username,
        "id": str(user.id),
    }
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": expire})
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
