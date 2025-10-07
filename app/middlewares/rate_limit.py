
# Contoh sederhana rate limit middleware (dummy, untuk pengembangan lebih lanjut gunakan package seperti slowapi)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.client import client_ip_dependency

class RateLimitMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		# Dummy: selalu izinkan, tambahkan logika limit sesuai kebutuhan
		# Untuk produksi, gunakan package seperti slowapi
		client_ip, client_ip_type = client_ip_dependency(request)
		request.state.client_ip = client_ip
		request.state.client_ip_type = client_ip_type
		response = await call_next(request)
		return response
