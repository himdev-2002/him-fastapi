# context_request.py
import contextvars
import random
import shortuuid
from fastapi import Request


# ContextVar untuk menyimpan request_id per-request
ctx_req_id: contextvars.ContextVar[str] = contextvars.ContextVar("req_id", default=None)
ctx_tx_id: contextvars.ContextVar[str] = contextvars.ContextVar("tx_id", default=None)
ctx_route: contextvars.ContextVar[str] = contextvars.ContextVar("route", default=None)
ctx_log_act: contextvars.ContextVar[str] = contextvars.ContextVar("log_act", default=None)
ctx_act_name: contextvars.ContextVar[str] = contextvars.ContextVar("act_name", default=None)
ctx_client_ip: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip", default=None)
ctx_client_ip_type: contextvars.ContextVar[str] = contextvars.ContextVar("client_ip_type", default=None)

def get_request_id() -> str:
    return ctx_req_id.get()

def reset_request_id(token: contextvars.Token[str]):
    ctx_req_id.reset(token)

def set_request_id(req_id: str) -> contextvars.Token[str]:
    token = ctx_req_id.set(req_id)
    return token

def get_tx_id() -> str:
    return ctx_tx_id.get()
        
def generate_tx_id(act:str) -> str:
    rand_digits = str(random.randint(1000, 9999))
    return f"{act}-{shortuuid.uuid()}-{rand_digits}"

def reset_tx_id(token: contextvars.Token[str]):
    ctx_tx_id.reset(token)

def set_tx_id(tx_id: str) -> contextvars.Token[str]:
    # print(f"Setting tx id: {tx_id}")
    if not tx_id or tx_id == '':
        tx_id = generate_tx_id(act="NONE")
    token = ctx_tx_id.set(tx_id)
    return token

def get_route() -> str:
    return ctx_route.get()

def reset_route(token: contextvars.Token[str]):
    ctx_route.reset(token)

def set_route(route: str) -> contextvars.Token[str]:
    token = ctx_route.set(route)
    return token

def get_client_ip() -> str:
    return ctx_client_ip.get()

def reset_client_ip(token: contextvars.Token[str]):
    ctx_client_ip.reset(token)

def set_client_ip(client_ip: str) -> contextvars.Token[str]:
    token = ctx_client_ip.set(client_ip)
    return token

def get_client_ip_type() -> str:
    return ctx_client_ip_type.get()

def reset_client_ip_type(token: contextvars.Token[str]):
    ctx_client_ip_type.reset(token)

def set_client_ip_type(client_ip_type: str) -> contextvars.Token[str]:
    token = ctx_client_ip_type.set(client_ip_type)
    return token

def get_log_act() -> str:
    return ctx_log_act.get()

def reset_log_act(token: contextvars.Token[str]):
    ctx_log_act.reset(token)

def set_log_act(log_act: str) -> contextvars.Token[str]:
    token = ctx_log_act.set(log_act)
    return token

def get_act_name() -> str:
    return ctx_act_name.get()

def reset_act_name(token: contextvars.Token[str]):
    ctx_act_name.reset(token)

def set_act_name(act_name: str) -> contextvars.Token[str]:
    token = ctx_act_name.set(act_name)
    return token