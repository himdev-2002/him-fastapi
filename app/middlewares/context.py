from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.client import client_ip_dependency
from app.utils.helpers import get_current_route
from app.core.context import set_request_id, get_request_id, set_client_ip, set_client_ip_type, set_route

class ContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # await set_request_id(request, call_next)
        request.state.req_id = get_request_id() or "-"
        client_ip, client_ip_type = client_ip_dependency(request)
        route = get_current_route(request)
        set_client_ip(client_ip)
        request.state.client_ip = client_ip or "-"
        set_client_ip_type(client_ip_type)
        request.state.client_ip_type = client_ip_type or "-"
        await set_route(route['path'])
        request.state.route = route['path'] or "-"
        return await call_next(request)