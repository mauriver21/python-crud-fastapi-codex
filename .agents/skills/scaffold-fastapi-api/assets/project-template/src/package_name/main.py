from fastapi import FastAPI

from {{package_name}}.api.router import router
from {{package_name}}.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(router)
    return app


app = create_app()

