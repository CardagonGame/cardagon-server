from fastapi import APIRouter
import tomllib

router = APIRouter(tags=["status"])
with open("pyproject.toml", "rb") as f:
    d = tomllib.load(f)
    version_string = d['project']['version']


@router.get("/status")
async def get_status():
    return {
        "status": "ok",
        "version": version_string,
    }
