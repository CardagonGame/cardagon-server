from fastapi import APIRouter
import importlib.metadata

router = APIRouter(tags=["status"])
version_string = importlib.metadata.version("cardagon-server")


@router.get("/status")
async def get_status():
    return {
        "status": "ok",
        "version": version_string,
    }
