
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	APP_NAME: str
	APP_VERSION: str
	ENV: str
	DB_URL: str
	DB_URL_ASYNC: str
	DB_MIGRATE_URL: str
	DB_TXONLY_URL: str
	DB_TXONLY_URL_ASYNC: str
	REDIS_HOST: str
	REDIS_PORT: int
	REDIS_DB: int
	REDIS_PASSWORD: str
	REDIS_USERNAME: str
	JWT_SECRET: str
	JWT_ALGORITHM: str
	JWT_EX_PATHS: list[str]
	JWT_ACCESS_EXPIRE_MINUTES: int = 15
	JWT_REFRESH_EXPIRE_MINUTES: int = 43200
	JWT_BLACKLIST_EXPIRE_SECONDS: int = 2592000
	LOG_LEVEL: str
	LOG_DIR: str = "."
	SWAGGER_URL: str = "/docs"
	REDOC_URL: str = "/redoc"
	LIMITER_ENABLED: bool = True 
	LIMITER_STORAGE_URI: str = "redis://localhost:6379/0"
	RATE_LIMIT_DEFAULT: str = "20/minute"
	RATE_LIMIT_HIGH: str = "100/minute"
	RATE_LIMIT_LOW: str = "5/minute"
	IP_WHITELIST: list[str] = []
	IP_BLACKLIST: list[str] = []
	DOMAIN_WHITELIST: list[str] = []
	DOMAIN_BLACKLIST: list[str] = []
	CORS_ALLOW_ORIGINS: list[str] = ["*"]
	CORS_ALLOW_METHODS: list[str] = ["*"]
	CORS_ALLOW_HEADERS: list[str] = ["*", "Authorization", "Content-Type"]
	CORS_ALLOW_CREDENTIALS: bool = True
	RUSTFS_ENDPOINT: str = "http://localhost:9000"
	RUSTFS_ACCESS_KEY: str = "4YW6g1Z5UoKGaTctPQD2"
	RUSTFS_SECRET_KEY: str = "mbLWARe0Crxvjo651DtnQiJBcMFf4uV8gOzSlEPT"
	RUSTFS_BUCKET: str = "him-fast-api"
	CELERY_BROKER_URL: str = "redis://localhost:6379/1"
	CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

	class Config:
		env_file = ".env"

settings = Settings()
