from fastapi import APIRouter

from app.dependencies.user import CurrentUserDep, get_current_user
from app.dto.user import UserPublic


router = APIRouter(tags=["users"])


@router.get("/me")
def read_user_me(user: CurrentUserDep) -> UserPublic:
    """
    Get current user.
    """
    print("Current user:", user)
    return user
