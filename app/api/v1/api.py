
from fastapi import APIRouter
from app.api.v1.routes import users, items
from app.utils.logger import log_api

log_api(
    msg="Starting Configure v1 Routes...",
    act="init_app",
    level="INFO"
)
api_router = APIRouter()
api_version = "v1"
prefix = f"/api/{api_version}"

log_api(
    msg="Configure v1 Users Routes...",
    act="init_app",
    level="INFO"
)
api_router.include_router(users.router, prefix=f"{prefix}", tags=["Users"])

log_api(
    msg="Configure v1 Items Routes...",
    act="init_app",
    level="INFO"
)
api_router.include_router(items.router, prefix=f"{prefix}", tags=["Items"])

log_api(
    msg="Configure v1 Routes Done.",
    act="init_app",
    level="INFO"
)