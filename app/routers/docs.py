from fastapi import APIRouter
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

router = APIRouter(tags=["docs"])


@router.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Cardagon - Swagger UI",
        swagger_favicon_url="https://placekitten.com/200/300",
    )


@router.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Cardagon - ReDoc",
        redoc_favicon_url="https://placekitten.com/200/300",
    )
