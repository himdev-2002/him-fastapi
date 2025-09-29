import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.logger import log_api

SQLI_PATTERNS = [
    r"(--|;|/\*|\*/|@@|char\(|nchar\(|varchar\(|alter |begin |cast\(|create |cursor |declare |delete |drop |end |exec |execute |fetch |insert |kill |open |select |sys |sysobjects|syscolumns|table |update )"
]

def has_sqli(payload: str) -> bool:
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, payload, re.IGNORECASE):
            return True
    return False

class SQLInjectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude by decorator
        # endpoint = None
        # if hasattr(request, 'scope') and 'endpoint' in request.scope:
        #     endpoint = request.scope['endpoint']
        # if endpoint and hasattr(endpoint, 'excluded_middlewares'):
        #     if 'SQLInjectionMiddleware' in endpoint.excluded_middlewares:
        #         return await call_next(request)

        # if request.method in ("POST", "PUT", "PATCH"):
        log_api(f"Checking for SQL Injection in request", act="sqli", level="DEBUG")
        body = await request.body()
        if has_sqli(body.decode(errors="ignore")):
            return JSONResponse(status_code=400, content={"detail": "Potential SQL Injection detected"})
        return await call_next(request)
