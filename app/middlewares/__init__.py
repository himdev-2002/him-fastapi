from app.utils.logger import log_api
from .ip_filter import IPFilterMiddleware
# Security headers middleware
# Security headers middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .cors import add_cors_middleware
from .logging import LoggingMiddleware

from .rate_limit import RateLimitMiddleware
from .jwt_auth import JWTAuthMiddleware
from .sql_injection import SQLInjectionMiddleware
from .xss import XSSMiddleware
from .context import ContextMiddleware
from .cleansing import CleansingMiddleware

def setup_middlewares(app):
	log_api(
		msg="Starting Configure Middlewares...",
		act="app",
		level="INFO"
	)
	# Context
	app.add_middleware(ContextMiddleware)
	# Logging
	app.add_middleware(LoggingMiddleware)
	# IP/domain whitelist/blacklist
	app.add_middleware(IPFilterMiddleware)
	# CORS
	add_cors_middleware(app)
	# Security headers
	app.add_middleware(SecurityHeadersMiddleware)
	# Rate limit (dummy, bisa diganti slowapi)
	app.add_middleware(RateLimitMiddleware)
	# JWT Auth (aktifkan jika ingin proteksi endpoint)
	app.add_middleware(JWTAuthMiddleware)
	# SQL Injection protection
	app.add_middleware(SQLInjectionMiddleware)
	# XSS protection
	app.add_middleware(XSSMiddleware)
	# Cleansing
	# app.add_middleware(CleansingMiddleware)
	log_api(
		msg="Configure Middlewares Done.",
		act="app",
		level="INFO"
	)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		response = await call_next(request)
		response.headers["X-Content-Type-Options"] = "nosniff"
		response.headers["X-Frame-Options"] = "DENY"
		response.headers["X-XSS-Protection"] = "1; mode=block"
		response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
		return response
