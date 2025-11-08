from fastapi import APIRouter

from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import CurrentUserDep, get_current_user
from app.dto.user import UserPublic


router = APIRouter(tags=["users"])


@router.get(f"{API_V1_PREFIX}/me")
def read_user_me(user: CurrentUserDep) -> UserPublic:
    """
    Get current user.
    """
    print("Current user:", user)
    return user
