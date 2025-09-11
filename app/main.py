import asyncio
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings

from app.middlewares.context import set_request_id
from app.api.v1.api import api_router
from app.middlewares import setup_middlewares
from app.utils.logger import log_api
from app.core import database
from app.core.redis_client import test_redis_connection
from app.utils.helpers import is_awaitable

if sys.platform.startswith("win"):
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


log_api(
	msg=f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} application...",
	act="init_app",
	level="INFO"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Run DB and Redis connectivity checks at application startup. Fail startup if tests fail."""
	log_api(msg="Running startup connectivity checks...", act="init_app", level="INFO")
	
	# Test Redis connection in a thread (avoid blocking event loop)
	try:
		ok_redis = await asyncio.get_event_loop().run_in_executor(None, test_redis_connection)
		if ok_redis is not None:
			raise Exception(f"Redis connection test returned False: {ok_redis}")
		log_api(msg="Redis connection OK", act="init_app", level="INFO")
	except Exception as exc:
		log_api(msg=f"Redis connection failed: {exc}", act="init_app", level="CRITICAL")
		raise

	# Test sync connection in a thread (avoid blocking event loop)
	try:
		ok_sync = await asyncio.get_event_loop().run_in_executor(None, database.test_sync_connection)
		if not ok_sync:
			raise Exception("Sync DB test returned False")
		log_api(msg="Sync DB connection OK", act="init_app", level="INFO")
	except Exception as exc:
		log_api(msg=f"Sync DB connection failed: {exc}", act="init_app", level="CRITICAL")
		raise

	# Test async connection directly
	try:
		ok_async = await database.test_async_connection()
		if not ok_async:
			raise Exception("Async DB test returned False")
		log_api(msg="Async DB connection OK", act="init_app", level="INFO")
	except Exception as exc:
		log_api(msg=f"Async DB connection failed: {exc}", act="init_app", level="CRITICAL")
		raise
	yield
	if is_awaitable(database.engine_sync.dispose()):
		await database.engine_sync.dispose()
	if is_awaitable(database.engine_async.dispose()):
		await database.engine_async.dispose()
	log_api(msg="Application shutdown", act="shutdown", level="INFO")
	
# @app.on_event("startup")
# async def startup_checks():
#     """Run DB connectivity checks at application startup. Fail startup if tests fail."""
#     log_api(msg="Running startup DB connectivity checks...", act="init_app", level="INFO")
#     # Test sync connection in a thread (avoid blocking event loop)
#     try:
#         ok_sync = await asyncio.get_event_loop().run_in_executor(None, database.test_sync_connection)
#         if not ok_sync:
#             raise Exception("Sync DB test returned False")
#         log_api(msg="Sync DB connection OK", act="init_app", level="INFO")
#     except Exception as exc:
#         log_api(msg=f"Sync DB connection failed: {exc}", act="init_app", level="CRITICAL")
#         raise

#     # Test async connection directly
#     try:
#         ok_async = await database.test_async_connection()
#         if not ok_async:
#             raise Exception("Async DB test returned False")
#         log_api(msg="Async DB connection OK", act="init_app", level="INFO")
#     except Exception as exc:
#         log_api(msg=f"Async DB connection failed: {exc}", act="init_app", level="CRITICAL")
#         raise
	
# @app.on_event("shutdown")
# def shutdown_event():
#         log_api(msg="Application shutdown", act="shutdown", level="INFO")

app = FastAPI(
	title=settings.APP_NAME,
	version=settings.APP_VERSION,
	docs_url=settings.SWAGGER_URL,
	redoc_url=settings.REDOC_URL,
	lifespan=lifespan
)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Tambahkan middleware
app.middleware("http")(set_request_id)
setup_middlewares(app)

log_api(
	msg="Starting Configure API Endpoints...",
	act="init_app",
	level="INFO"
)
app.include_router(api_router)

log_api(
	msg=f"Done initializing {settings.APP_NAME} v{settings.APP_VERSION} application.",
	act="init_app",
	level="INFO"
)