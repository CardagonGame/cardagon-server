from fastapi import APIRouter
import tomllib

router = APIRouter(tags=["status"])
with open("pyproject.toml", "rb") as project_file:
    project_dict = tomllib.load(project_file)
    version_string = project_dict['project']['version']


@router.get("/status")
async def get_status():
    return {
        "status": "ok",
        "version": version_string,
    }
