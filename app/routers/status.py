import tomllib

from fastapi import APIRouter

from app.dependencies.static import API_V1_PREFIX

router = APIRouter(tags=["status"])

with open("pyproject.toml", "rb") as project_file:
    project_dict = tomllib.load(project_file)
    version_string = project_dict["project"]["version"]


@router.get(f"{API_V1_PREFIX}/status")
async def get_status():
    return {
        "status": "ok",
        "version": version_string,
    }
