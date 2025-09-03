
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
import jwt
from fastapi.routing import APIRoute



class JWTAuthMiddleware(BaseHTTPMiddleware):
    def is_exempt(self, path: str) -> bool:
        for prefix in getattr(settings, "JWT_EXEMPT_PATHS", []):
            if path.startswith(prefix) or not path.startswith("/api"):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        # Exclude by decorator
        endpoint = None
        if hasattr(request, 'scope') and 'endpoint' in request.scope:
            endpoint = request.scope['endpoint']
        if endpoint and hasattr(endpoint, 'excluded_middlewares'):
            if 'JWTAuthMiddleware' in endpoint.excluded_middlewares:
                return await call_next(request)

        if self.is_exempt(request.url.path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            request.state.user = payload
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
