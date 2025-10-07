import time
from fastapi import Request

from app.utils.logger import log_api
from app.core.context import set_client_ip, set_client_ip_type

current_client_info = [None, None]

def get_client_ip(request: Request) -> [str, str]:
    """Extract client IP from request"""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",").strip()
        return client_ip, "X-Forwarded-For" 
    
    if request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP"), "X-Real-IP"
    
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("CF-Connecting-IP"), "CF-Connecting-IP"
    
    return request.client.host, "Client-IP"

def client_ip_dependency(request: Request) -> [str, str]:
    """Dependency that returns the client IP"""
    current_client_info = get_client_ip(request)
    set_client_ip(current_client_info[0])
    set_client_ip_type(current_client_info[1])
    request.state.client_ip = current_client_info[0]
    request.state.client_ip_type = current_client_info[1]
    log_api(
        f"Client IP: {current_client_info[0]} {current_client_info[1]}",
        act="info",
        level="DEBUG",
        client_ip=current_client_info[0],
        client_ip_type=current_client_info[1]
    )
    return current_client_info

# def rate_limit(request: Request):
#     client_ip = get_client_ip(request)
#     current_time = time.time()
    
#     if client_ip in rate_limit_storage:
#         count, start_time = rate_limit_storage[client_ip]
        
#         # Reset if window has passed
#         if current_time - start_time > RATE_LIMIT_WINDOW:
#             rate_limit_storage[client_ip] = (1, current_time)
#         else:
#             # Increment count
#             count += 1
#             if count > RATE_LIMIT:
#                 raise HTTPException(
#                     status_code=429, 
#                     detail="Too many requests. Please try again later."
#                 )
#             rate_limit_storage[client_ip] = (count, start_time)
#     else:
#         # First request from this IP
#         rate_limit_storage[client_ip] = (1, current_time)
    
#     return client_ip