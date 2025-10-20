from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
import jwt
from app.services.auth import JWTSession
from app.utils.logger import log_api



class JWTAuthMiddleware(BaseHTTPMiddleware):
    def is_exempt(self, path: str) -> bool:
        for prefix in getattr(settings, "JWT_EX_PATHS", []):
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
        print(f"auth_header: {auth_header}")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        token = auth_header.split(" ", 1)[1]
        log_api(f"Token: {token}", act="auth", level="DEBUG")
        try:
            # Cek whitelist dan blacklist
            is_refresh = request.url.path.endswith("/auth/refresh")
            payload = JWTSession.verify_access_token(token, is_refresh)
            if not payload:
                return JSONResponse(status_code=401, content={"detail": "Access Token not valid"})
            log_api(f"Payload: {payload}", act="auth", level="DEBUG")
            user_id = int(payload["sub"])
            jti = payload.get("jti")
            _key = payload.get("_key")
            # log_api(f"User ID: {user_id}", act="auth", level="DEBUG")
            # log_api(f"JTI: {jti}", act="auth", level="DEBUG")
            # log_api(f"Key: {_key}", act="auth", level="DEBUG")
            request.state.user = user_id
            request.state.req_id = _key
            request.state.jti = jti
            request.state.payload = payload
        except Exception as e:
            log_api(f"Failed to verify access token: {e}", act="auth", level="ERROR")
            return JSONResponse(status_code=401, content={"detail": "Invalid Access Token"})
        log_api(f"Access token verified", act="auth", level="DEBUG")
        response = await call_next(request)
        return response
