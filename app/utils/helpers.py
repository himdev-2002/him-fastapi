
# Tambahkan helper function jika diperlukan
import inspect
import shortuuid
from fastapi import Request

def is_awaitable(obj):
    return inspect.isawaitable(obj) or hasattr(obj, "__await__")


def verify_password(plain_password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    Prefers passlib.hash.bcrypt.verify if available, otherwise uses bcrypt.checkpw.
    """
    try:
        from passlib.hash import bcrypt
        return bcrypt.verify(plain_password, hashed)
    except Exception:
        try:
            import bcrypt as _bcrypt
            return _bcrypt.checkpw(plain_password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            # If neither library is available, return False
            return False
        
def generate_tx_id(act:str) -> str:
    return f"tx-{act}-{shortuuid.uuid()}"

def get_current_route(request: Request) -> dict:
    """
    Ambil informasi route & method dari Request.
    """
    return {
        "full_url": str(request.url),
        "path": request.scope.get("path"),
        "method": request.method,
        "endpoint": request.scope.get("endpoint").__name__ if request.scope.get("endpoint") else None,
        "route_name": request.scope.get("route").name if request.scope.get("route") else None,
    }