
from pydantic_settings import BaseSettings





class Settings(BaseSettings):
	APP_NAME: str
	APP_VERSION: str
	ENV: str
	DB_URL: str
	JWT_SECRET: str
	JWT_ALGORITHM: str
	JWT_EXEMPT_PATHS: list[str]
	LOG_LEVEL: str
	SWAGGER_URL: str = "/docs"
	REDOC_URL: str = "/redoc"
	IP_WHITELIST: list[str] = []
	IP_BLACKLIST: list[str] = []
	DOMAIN_WHITELIST: list[str] = []
	DOMAIN_BLACKLIST: list[str] = []
	CORS_ALLOW_ORIGINS: list[str] = ["*"]
	CORS_ALLOW_METHODS: list[str] = ["*"]
	CORS_ALLOW_HEADERS: list[str] = ["*"]
	CORS_ALLOW_CREDENTIALS: bool = True

	class Config:
		env_file = ".env"

settings = Settings()
