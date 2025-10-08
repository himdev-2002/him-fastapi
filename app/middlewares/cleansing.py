
# Contoh sederhana rate limit middleware (dummy, untuk pengembangan lebih lanjut gunakan package seperti slowapi)
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.context import reset_act_name, reset_client_ip_type, reset_request_id, reset_tx_id, reset_route, reset_client_ip

class CleansingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		response = await call_next(request)
		if getattr(request.state, "req_token", None):
			reset_request_id(request.state.req_token)
		if getattr(request.state, "tx_token", None):
			reset_tx_id(request.state.tx_token)
		if getattr(request.state, "route_token", None):
			reset_route(request.state.route_token)
		if getattr(request.state, "client_ip_token", None):
			reset_client_ip(request.state.client_ip_token)
		if getattr(request.state, "client_ip_type_token", None):
			reset_client_ip_type(request.state.client_ip_type_token)
		if getattr(request.state, "act_token", None):
			reset_act_name(request.state.act_token)
		return response