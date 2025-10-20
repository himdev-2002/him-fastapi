import random
from fastapi import Request
import shortuuid
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.client import client_ip_dependency
from app.utils.helpers import get_current_route, get_route_name, get_route_tags
from app.core.context import reset_request_id, set_act_name, get_request_id, set_client_ip, set_client_ip_type, set_route, generate_tx_id, set_tx_id, set_request_id, reset_tx_id, reset_route, reset_client_ip, reset_client_ip_type, reset_act_name, set_log_act, reset_log_act

class ContextMiddleware(BaseHTTPMiddleware):
	def __init__(self, app):
		super().__init__(app)

	async def dispatch(self, request: Request, call_next):
		# await set_request_id(request, call_next)
		if not getattr(request.state, "req_id", None):
			req_id = request.headers.get("X-Request-ID", f"{shortuuid.uuid()}-{id(request)}")
			if not req_id or req_id == '':
				rand_digits = str(random.randint(1000, 9999))
				req_id = f"{shortuuid.uuid()}-{rand_digits}"
			request.state.req_id = req_id
		req_id = request.state.req_id
		req_token = set_request_id(req_id)
		request.state.req_token = req_token or None

		route_tags = get_route_tags(request)
		request.state.route_tags = route_tags or None
		# print(f"route_tags: {route_tags}")
	
		log_act = route_tags[len(route_tags)-1] if route_tags else None
		request.state.log_act = log_act or None
		log_act_token = set_log_act(log_act)
		request.state.log_act_token = log_act_token or None

		route_name = get_route_name(request)
		# print(f"route_tags: {route_tags}")
		request.state.act_name = route_name or None
		act_token = set_act_name(route_name)   
		request.state.act_token = act_token or None

		tx_id = generate_tx_id(act=route_name)
		request.state.tx_id = tx_id or None
		tx_token = set_tx_id(tx_id)
		request.state.tx_token = tx_token or None

		request.state.req_id = get_request_id() or None
		client_ip, client_ip_type = client_ip_dependency(request)

		client_ip_token = set_client_ip(client_ip)
		request.state.client_ip_token = client_ip_token or None

		client_ip_type_token = set_client_ip_type(client_ip_type)
		request.state.client_ip_type_token = client_ip_type_token or None

		route = get_current_route(request)
		route_token = set_route(route['path'])
		request.state.route_token = route_token or None
		# print("ContextMiddleware",request.state.__dict__)
		response = await call_next(request)
		
		if req_token:
			reset_request_id(req_token)
		if tx_token:
			reset_tx_id(tx_token)
		if route_token:
			reset_route(route_token)
		if client_ip_token:
			reset_client_ip(client_ip_token)
		if client_ip_type_token:
			reset_client_ip_type(client_ip_type_token)
		if act_token:
			reset_act_name(act_token)
		if log_act_token:
			reset_log_act(log_act_token)
		return response