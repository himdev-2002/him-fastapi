from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings
import ipaddress

class IPFilterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.whitelist = set(getattr(settings, "IP_WHITELIST", []))
        self.blacklist = set(getattr(settings, "IP_BLACKLIST", []))
        self.domain_whitelist = set(getattr(settings, "DOMAIN_WHITELIST", []))
        self.domain_blacklist = set(getattr(settings, "DOMAIN_BLACKLIST", []))

    async def dispatch(self, request: Request, call_next):
        # Exclude by decorator
        endpoint = None
        if hasattr(request, 'scope') and 'endpoint' in request.scope:
            endpoint = request.scope['endpoint']
        if endpoint and hasattr(endpoint, 'excluded_middlewares'):
            if 'IPFilterMiddleware' in endpoint.excluded_middlewares:
                return await call_next(request)

        client_ip = request.client.host
        host = request.headers.get("host", "")
        # Blacklist check
        if client_ip in self.blacklist or host in self.domain_blacklist:
            return JSONResponse(status_code=403, content={"detail": "Access denied (blacklist)"})
        # Whitelist check (if set, only allow listed)
        if self.whitelist and client_ip not in self.whitelist:
            return JSONResponse(status_code=403, content={"detail": "Access denied (not whitelisted)"})
        if self.domain_whitelist and host not in self.domain_whitelist:
            return JSONResponse(status_code=403, content={"detail": "Access denied (domain not whitelisted)"})
        return await call_next(request)
