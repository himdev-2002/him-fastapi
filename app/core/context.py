# context_request.py
import contextvars
import random
import shortuuid
from fastapi import Request


# ContextVar untuk menyimpan request_id per-request
ctx_req_id: contextvars.ContextVar[str] = contextvars.ContextVar("req_id", default="-")
ctx_tx_id: contextvars.ContextVar[str] = contextvars.ContextVar("tx_id", default="-")
ctx_route: contextvars.ContextVar[str] = contextvars.ContextVar("route", default="-")
ctx_client_ip: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip", default="-")
ctx_client_ip_type: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip_type", default="-")

def get_request_id() -> str:
    return ctx_req_id.get()

async def set_request_id(request: Request, call_next):
    # Bisa pakai header `X-Request-ID`, atau auto generate
    if not getattr(request.state, "req_id", None):
        req_id = request.headers.get("X-Request-ID", f"{shortuuid.uuid()}-{id(request)}")
        if not req_id or req_id == '':
            rand_digits = str(random.randint(1000, 9999))
            req_id = f"{shortuuid.uuid()}-{rand_digits}"
        request.state.req_id = req_id
    req_id = request.state.req_id
    token = ctx_req_id.set(req_id)
    response = await call_next(request)
    ctx_req_id.reset(token)
    return response

def get_tx_id() -> str:
    return ctx_tx_id.get()
        
def generate_tx_id(act:str) -> str:
    rand_digits = str(random.randint(1000, 9999))
    return f"{act}-{shortuuid.uuid()}-{rand_digits}"

async def reset_tx_id(token: contextvars.Token[str]):
    ctx_tx_id.reset(token)

async def set_tx_id(tx_id: str) -> contextvars.Token[str]:
    # print(f"Setting tx id: {tx_id}")
    if not tx_id or tx_id == '':
        tx_id = generate_tx_id(act="NONE")
    token = ctx_tx_id.set(tx_id)
    return token

def get_route() -> str:
    return ctx_route.get()

async def reset_route(token: contextvars.Token[str]):
    ctx_route.reset(token)

async def set_route(route: str) -> contextvars.Token[str]:
    token = ctx_route.set(route)
    return token

def get_client_ip() -> str:
    return ctx_client_ip.get()

async def reset_client_ip(token: contextvars.Token[str]):
    ctx_client_ip.reset(token)

def set_client_ip(client_ip: str) -> contextvars.Token[str]:
    ip = ctx_client_ip.set(client_ip)
    return ip

def get_client_ip_type() -> str:
    return ctx_client_ip_type.get()

async def reset_client_ip_type(token: contextvars.Token[str]):
    ctx_client_ip_type.reset(token)

def set_client_ip_type(client_ip_type: str) -> contextvars.Token[str]:
    ip_type = ctx_client_ip_type.set(client_ip_type)
    return ip_type