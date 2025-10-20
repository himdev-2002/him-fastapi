
from fastapi import APIRouter
from app.api.v1.routes import user, auth, public, profile
from app.utils.logger import log_api

log_api(
    msg="Starting Configure v1 Routes...",
    act="app",
    level="INFO"
)
api_router = APIRouter()
api_version = "v1"
prefix = f"/api/{api_version}"

log_api(
    msg="Configure v1 Public Routes...",
    act="app",
    level="INFO"
)

api_router.include_router(public.router, prefix=f"{prefix}", tags=[api_version])


log_api(
    msg="Configure v1 Auth Routes...",
    act="app",
    level="INFO"
)

api_router.include_router(auth.router, prefix=f"{prefix}", tags=[api_version])

log_api(
    msg="Configure v1 User Routes...",
    act="app",
    level="INFO"
)

api_router.include_router(user.router, prefix=f"{prefix}", tags=[api_version])

log_api(
    msg="Configure v1 Profile Routes...",
    act="app",
    level="INFO"
)

api_router.include_router(profile.router, prefix=f"{prefix}", tags=[api_version])

# log_api(
#     msg="Configure v1 Item Routes...",
#     act="app",
#     level="INFO"
# )
# api_router.include_router(item.router, prefix=f"{prefix}", tags=["item"])

log_api(
    msg="Configure v1 Routes Done.",
    act="app",
    level="INFO"
)