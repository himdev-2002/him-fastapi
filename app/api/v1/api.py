
from fastapi import APIRouter
from app.api.v1.routes import users, items

api_router = APIRouter()
api_version = "v1"
prefix = f"/api/{api_version}"
api_router.include_router(users.router, prefix=f"{prefix}", tags=["Users"])
api_router.include_router(items.router, prefix=f"{prefix}", tags=["Items"])
