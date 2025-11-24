import re
from typing import Any
from urllib.parse import unquote
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.logger import log_api

SQLI_PATTERNS = [
    r"(--|;|/\*|\*/|@@|char\(|nchar\(|varchar\(|alter |begin |cast\(|create |cursor |declare |delete |drop |end |exec |execute |fetch |insert |kill |open |select |sys |sysobjects|syscolumns|table |update )"
]


def has_sqli(payload: str) -> bool:
    """
    Check if a payload contains SQL injection patterns.
    
    Args:
        payload (str): The string to check for SQL injection patterns.
    
    Returns:
        bool: True if SQL injection pattern is detected, False otherwise.
    """
    if not payload:
        return False
    
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, payload, re.IGNORECASE):
            return True
    return False


def check_value_for_sqli(value: Any, source: str) -> tuple[bool, str]:
    """
    Check a single value for SQL injection patterns.
    
    Args:
        value (Any): The value to check (will be converted to string).
        source (str): The source of the value (for logging purposes).
    
    Returns:
        tuple[bool, str]: (is_sqli_detected, detected_value)
    """
    if value is None:
        return False, ""
    
    # Convert to string and URL decode
    value_str = str(value)
    decoded_value = unquote(value_str)
    
    if has_sqli(decoded_value):
        return True, decoded_value
    
    return False, ""


class SQLInjectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and prevent SQL injection attacks.
    
    Checks multiple request components for SQL injection patterns:
    - URL path and route
    - Path parameters (from URL path segments)
    - Query parameters (from URL query string)
    - Request body (for POST, PUT, PATCH requests)
    
    Skips checking file uploads (multipart/form-data) as they contain binary data.
    Only validates non-file payloads for SQL injection patterns.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and check for SQL injection in all components.
        
        Args:
            request (Request): The incoming HTTP request.
            call_next: The next middleware or route handler.
        
        Returns:
            Response: Either a 400 error response if SQL injection is detected,
                     or the response from the next handler.
        """
        # Exclude by decorator
        # endpoint = None
        # if hasattr(request, 'scope') and 'endpoint' in request.scope:
        #     endpoint = request.scope['endpoint']
        # if endpoint and hasattr(endpoint, 'excluded_middlewares'):
        #     if 'SQLInjectionMiddleware' in endpoint.excluded_middlewares:
        #         return await call_next(request)

        log_api(
            f"Checking for SQL Injection in request: {request.method} {request.url.path}",
            act="sqli",
            level="DEBUG"
        )

        # Check URL path and route
        url_path = request.url.path
        is_sqli, detected_value = check_value_for_sqli(url_path, "URL path")
        if is_sqli:
            log_api(
                f"SQL injection detected in URL path: {detected_value}",
                act="sqli",
                level="WARNING"
            )
            return JSONResponse(
                status_code=400,
                content={"detail": "Potential SQL Injection detected in URL path"}
            )

        # Check path parameters
        if hasattr(request, "path_params") and request.path_params:
            for param_name, param_value in request.path_params.items():
                is_sqli, detected_value = check_value_for_sqli(
                    param_value,
                    f"path parameter '{param_name}'"
                )
                if is_sqli:
                    log_api(
                        f"SQL injection detected in path parameter '{param_name}': {detected_value}",
                        act="sqli",
                        level="WARNING"
                    )
                    return JSONResponse(
                        status_code=400,
                        content={
                            "detail": f"Potential SQL Injection detected in path parameter '{param_name}'"
                        }
                    )

        # Check query parameters
        if request.query_params:
            for param_name, param_value in request.query_params.items():
                is_sqli, detected_value = check_value_for_sqli(
                    param_value,
                    f"query parameter '{param_name}'"
                )
                if is_sqli:
                    log_api(
                        f"SQL injection detected in query parameter '{param_name}': {detected_value}",
                        act="sqli",
                        level="WARNING"
                    )
                    return JSONResponse(
                        status_code=400,
                        content={
                            "detail": f"Potential SQL Injection detected in query parameter '{param_name}'"
                        }
                    )

        # Check request body (skip for file uploads)
        content_type = request.headers.get("content-type", "").lower()
        if content_type.startswith("multipart/form-data"):
            log_api(
                f"Skipping SQL injection check for file upload request",
                act="sqli",
                level="DEBUG"
            )
            return await call_next(request)

        # Check body for non-file requests
        body = await request.body()
        if body:
            body_str = body.decode(errors="ignore")
            is_sqli, detected_value = check_value_for_sqli(body_str, "request body")
            if is_sqli:
                log_api(
                    f"SQL injection detected in request body: {detected_value[:100]}...",
                    act="sqli",
                    level="WARNING"
                )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Potential SQL Injection detected in request body"}
                )
            
            # Restore body so endpoint can read it
            # async def receive() -> dict:
            #     return {"type": "http.request", "body": body}
            
            # request._receive = receive
        
        return await call_next(request)
