
# Tambahkan helper function jika diperlukan
import inspect
import shortuuid
from fastapi import Request
from passlib.hash import bcrypt
import bcrypt as _bcrypt

from app.middlewares.context import generate_tx_id, reset_route, reset_tx_id, set_route, set_tx_id

def is_awaitable(obj):
    return inspect.isawaitable(obj) or hasattr(obj, "__await__")

def hash_password(password: str) -> str:
    try:
        return bcrypt.hash(password)
    except Exception as e:
        print(f"Error during password hashing: {e}")
        print(f"Using bcrypt library")
        try:
            return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        except Exception as e:
            print(f"Error during password hashing: {e}")
            return None

def verify_password(plain_password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    Prefers passlib.hash.bcrypt.verify if available, otherwise uses bcrypt.checkpw.
    """
    try:
        return bcrypt.verify(plain_password, hashed)
    except Exception as e:
        print(f"Error during password verification: {e}")
        print(f"Using bcrypt library")
        try:
            return _bcrypt.checkpw(plain_password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            print(f"Error during password verification: {e}")
            # If neither library is available, return False
            return False

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

async def init_route(request: Request, user: str, parent_act: str, act: str) -> tuple[str, dict, str, str]:
    tx_id = generate_tx_id(act=act)
    route = get_current_route(request)
    setattr(request.state, "user", user)
    setattr(request.state, "tx_id", tx_id)
    setattr(request.state, "act", parent_act)
    tx_token = await set_tx_id(tx_id)
    route_token = await set_route(route['path'])
    return tx_id, route, tx_token, route_token

async def end_route(tx_token: str, route_token: str) -> None:
    await reset_tx_id(tx_token)
    await reset_route(route_token)