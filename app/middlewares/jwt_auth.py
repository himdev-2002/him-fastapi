from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
import jwt
from app.services.auth_service import JWTSession
from app.utils.logger import log_api



class JWTAuthMiddleware(BaseHTTPMiddleware):
    def is_exempt(self, path: str) -> bool:
        for prefix in getattr(settings, "JWT_EXEMPT_PATHS", []):
            # print(f"Checking exemption for path: {path} against prefix: {prefix}")
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
        log_api(f"Token: {token}", act="auth", level="DEBUG")
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            log_api(f"Payload: {payload}", act="auth", level="DEBUG")
            user_id = int(payload["sub"])
            jti = payload.get("jti")
            log_api(f"User ID: {user_id}", act="auth", level="DEBUG")
            log_api(f"JTI: {jti}", act="auth", level="DEBUG")
            # Cek whitelist dan blacklist
            if not JWTSession.verify_access_token(token, user_id):
                return JSONResponse(status_code=401, content={"detail": "Token not valid (whitelist/blacklist)"})
            request.state.user = payload
        except Exception as e:
            log_api(f"Failed to verify access token: {e}", act="auth", level="ERROR")
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        log_api(f"Access token verified", act="auth", level="DEBUG")
        response = await call_next(request)
        return response
