


import time
import uuid
import random
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.utils.logger import log_api

class LoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		# Exclude by decorator
		endpoint = None
		if hasattr(request, 'scope') and 'endpoint' in request.scope:
			endpoint = request.scope['endpoint']
		if endpoint and hasattr(endpoint, 'excluded_middlewares'):
			if 'LoggingMiddleware' in endpoint.excluded_middlewares:
				return await call_next(request)

		# Generate request_id only once per request and store in request.state
		if not hasattr(request.state, "request_id"):
			rand_digits = str(random.randint(1000, 9999))
			request.state.request_id = f"{uuid.uuid4()}-{rand_digits}"
		request_id = request.state.request_id
		start_time = time.time()
		user = getattr(request.state, "user", None)
		user_info = user.get("sub") if isinstance(user, dict) and "sub" in user else "anonymous"
		response = await call_next(request)
		process_time = (time.time() - start_time) * 1000
		route = request.url.path
		msg = f"{request.method} {route} completed_in={process_time:.2f}ms status_code={response.status_code}"
		log_api(
			msg=msg,
			request_id=request_id,
			user=user_info,
			route=route,
			level="INFO"
		)
		return response
