from typing import Any
# Fungsi decorator untuk mengaplikasikan middleware pada endpoint tertentu

# Decorator untuk mengecualikan middleware tertentu pada endpoint
def exclude_middlewares(middleware_names: list[str]):
    def decorator(endpoint_func):
        setattr(endpoint_func, "excluded_middlewares", set(middleware_names))
        return endpoint_func
    return decorator

from fastapi import Request, Response
from functools import wraps
from typing import Callable, List

# Fungsi decorator untuk mengaplikasikan middleware pada endpoint tertentu

def use_middlewares(middlewares: List[Callable]):
    def decorator(endpoint_func):
        @wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            response: Response = None
            # Jalankan setiap middleware secara berurutan
            for middleware in middlewares:
                result = await middleware(request)
                if result is not None:
                    return result  # Jika middleware return response, hentikan
            response = await endpoint_func(*args, **kwargs)
            return response
        return wrapper
    return decorator
