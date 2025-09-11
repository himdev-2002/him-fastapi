


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

		start_time = time.time()
		response = await call_next(request)
		process_time = (time.time() - start_time) * 1000
		route = request.url.path
		user = getattr(request.state, "user", None)
		act = getattr(request.state, "act", None)
		tx_id = getattr(request.state, "tx_id", None)
		msg = f"{request.method} {route} completed_in={process_time:.2f}ms status_code={response.status_code}"
		log_api(
			msg=msg,
			user=user,
			route=route,
			act=act,
			tx_id=tx_id,
			level="INFO"
		)
		return response
