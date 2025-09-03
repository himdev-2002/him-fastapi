

from fastapi import FastAPI
from app.core.config import settings

from app.api.v1.api import api_router
from app.middlewares import setup_middlewares
from app.utils.logger import log_api


log_api(
    msg=f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} application...",
    act="init_app",
    level="INFO"
)
app = FastAPI(
	title=settings.APP_NAME,
    version=settings.APP_VERSION,
	docs_url=settings.SWAGGER_URL,
	redoc_url=settings.REDOC_URL
)

setup_middlewares(app)

log_api(
    msg="Starting Configure API Endpoints...",
    act="init_app",
    level="INFO"
)
app.include_router(api_router)

log_api(
    msg=f"Done initializing {settings.APP_NAME} v{settings.APP_VERSION} application.",
    act="init_app",
    level="INFO"
)