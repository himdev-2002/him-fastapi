from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import re

XSS_PATTERNS = [
    r"<script.*?>.*?</script>",
    r"javascript:",
    r"onerror=|onload=|onmouseover=|onfocus=|onblur="
]

def has_xss(payload: str) -> bool:
    for pattern in XSS_PATTERNS:
        if re.search(pattern, payload, re.IGNORECASE):
            return True
    return False

from fastapi.routing import APIRoute

class XSSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude by decorator
        # endpoint = None
        # if hasattr(request, 'scope') and 'endpoint' in request.scope:
        #     endpoint = request.scope['endpoint']
        # if endpoint and hasattr(endpoint, 'excluded_middlewares'):
        #     if 'XSSMiddleware' in endpoint.excluded_middlewares:
        #         return await call_next(request)

        # if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()
        if has_xss(body.decode(errors="ignore")):
            return JSONResponse(status_code=400, content={"detail": "Potential XSS detected"})
        return await call_next(request)
