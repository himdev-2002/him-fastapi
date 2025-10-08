# app/core/rate_limit.py
import asyncio
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response, status

from app.utils.client import client_ip_dependency
from app.schemas.response import NoDataResponse, SingleErrorResponse
from app.utils.logger import log_api
from app.middlewares.context import set_client_ip, set_client_ip_type, set_route
from app.utils.helpers import get_current_route
from app.core.constants import RES_CODE
from app.core.config import settings
from app.core.redis_client import REDIS_KEY_PREFIX


def client_ip_dependency_limiter(request: Request) -> str:
	"""Dependency that returns the client IP"""
	client_ip, client_ip_type = client_ip_dependency(request)
	PREFIX = ""
	# if settings.LIMITER_STORAGE_URI:
	# 	PREFIX = REDIS_KEY_PREFIX+":LIMITER:"
	return PREFIX + "_".join([client_ip, client_ip_type])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
	"""
	Build a simple JSON response that includes the details of the rate limit
	that was hit. If no limit is hit, the countdown is added to headers.
	"""
	# client_ip, client_ip_type = client_ip_dependency(request)
	# route = get_current_route(request)
	# set_client_ip(client_ip)
	# set_client_ip_type(client_ip_type)
	# asyncio.run(set_route(route['path']))	
	code = RES_CODE.SYSTEM+RES_CODE.LIMITER+1
	log_api(
		msg=f"Rate limit exceeded [{code}]: {exc.detail}",
		act="limiter", 
		level="CRITICAL"
	)

	ret = NoDataResponse(
		tx= getattr(request.state, "tx_id", None),
		req= getattr(request.state, "req_id", None),
		code=code,
		stat=False,
		msg=f"Rate limit exceeded: {exc.detail}"
	)
	# Create a user-friendly response    
	response = JSONResponse(
		status_code=status.HTTP_429_TOO_MANY_REQUESTS,
		content=ret.model_dump()
	)
	response = request.app.state.limiter._inject_headers(
		response, request.state.view_rate_limit
	)
	return response
	
LIMITER_KEY_PREFIX = settings.APP_NAME.replace(" ", "_").lower()
# Initialize the rate limiter with a function to get the client's IP address
if settings.LIMITER_STORAGE_URI:
	log_api(f"Using Redis as rate limiter storage", level="DEBUG")
	limiter = Limiter(key_func=client_ip_dependency_limiter, enabled=settings.LIMITER_ENABLED, 
		storage_uri=settings.LIMITER_STORAGE_URI,
		key_prefix=LIMITER_KEY_PREFIX
	)
else:	
	log_api(f"Using memory as rate limiter storage", level="DEBUG")
	limiter = Limiter(key_func=client_ip_dependency_limiter, enabled=settings.LIMITER_ENABLED,
		key_prefix=LIMITER_KEY_PREFIX
	)

# Define a function to configure rate limiting for a FastAPI app
def configure_limiter(app):
	app.state.limiter = limiter
	app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
