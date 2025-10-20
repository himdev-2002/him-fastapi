
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def add_cors_middleware(app):
	# print(f"Adding CORS middleware with settings: {settings.CORS_ALLOW_ORIGINS}, {settings.CORS_ALLOW_CREDENTIALS}, {settings.CORS_ALLOW_METHODS}, {settings.CORS_ALLOW_HEADERS}")
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.CORS_ALLOW_ORIGINS,
		allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
		allow_methods=settings.CORS_ALLOW_METHODS,
		allow_headers=settings.CORS_ALLOW_HEADERS,
	)
