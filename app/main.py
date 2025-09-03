

from fastapi import FastAPI
from app.core.config import settings

from app.api.v1.api import api_router
from app.middlewares import setup_middlewares



app = FastAPI(
	title=settings.APP_NAME,
    version=settings.APP_VERSION,
	docs_url=settings.SWAGGER_URL,
	redoc_url=settings.REDOC_URL
)
setup_middlewares(app)
app.include_router(api_router)
