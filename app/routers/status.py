from fastapi import APIRouter

from app.dependencies.static import API_V1_PREFIX
from app.settings import PROJECT_VERSION

router = APIRouter(tags=["status"])


@router.get(f"{API_V1_PREFIX}/status")
async def get_status():
    return {
        "status": "ok",
        "version": PROJECT_VERSION,
    }
