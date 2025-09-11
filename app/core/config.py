
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	APP_NAME: str
	APP_VERSION: str
	ENV: str
	DB_URL: str
	DB_URL_ASYNC: str
	DB_MIGRATE_URL: str
	REDIS_HOST: str
	REDIS_PORT: int
	REDIS_DB: int
	REDIS_PASSWORD: str
	REDIS_USERNAME: str
	JWT_SECRET: str
	JWT_ALGORITHM: str
	JWT_EXEMPT_PATHS: list[str]
	JWT_ACCESS_EXPIRE_MINUTES: int = 15
	JWT_REFRESH_EXPIRE_MINUTES: int = 43200
	JWT_BLACKLIST_EXPIRE_SECONDS: int = 2592000
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
