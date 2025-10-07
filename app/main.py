import asyncio
import sys
from contextlib import asynccontextmanager
import traceback
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
# import the module we want to modify
import fastapi.openapi.utils as fau
from app.core.config import settings

from app.core.context import set_request_id
from app.api.v1 import api_router
from app.middlewares import setup_middlewares
from app.utils.logger import log_api
from app.core import database
from app.core.redis_client import test_redis_connection
from app.utils.helpers import is_awaitable
from app.core.error import I18nErrorFormatter
from app.schemas.response import NoDataResponse, SingleDataResponse, SingleErrorResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.limiter import configure_limiter

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
	lifespan=lifespan,
)

configure_limiter(app)

# print(SingleErrorResponse.model_json_schema())
# and override the schema
fau.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
	"properties": SingleErrorResponse.model_json_schema()["properties"],
    # "properties": {
	# 	# "detail": SingleErrorResponse.model_json_schema()
	# 	"tx": {"title": "Transaction ID", "type": "string"},
	# 	"req": {"title": "Request ID", "type": "string"},
	# 	"stat": {"title": "Status", "type": "boolean"},
	# 	"msg": {"title": "Message", "type": "string"},
	# 	"code": {"title": "Code", "type": "integer"},
	# 	"err": {"title": "Errors", "type": "object"},
	# },
}

# fau.validation_error_definition = {
#     "title": "ValidationError",
#     "type": "object",
#     "properties": {
# 		# "detail": SingleErrorResponse.model_json_schema()
# 		"tx": {"title": "Transaction ID", "type": "string"},
# 		"req": {"title": "Request ID", "type": "string"},
# 		"stat": {"title": "Status", "type": "boolean"},
# 		"msg": {"title": "Message", "type": "string"},
# 		"code": {"title": "Code", "type": "integer"},
# 		"err": {"title": "Errors", "type": "object"},
# 	},
# }

# Exception handler untuk semua exception
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
	error_traceback = traceback.format_exc()
	log_api(
		msg=f"Unhandled exception: {str(exc)}",
		act="exception",
		level="ERROR"
	)
	
	return JSONResponse(
		status_code=500,
		content={
			"message": "Internal Server Error",
			"detail": str(exc),
			"traceback": error_traceback.split("\n") if settings.LOG_LEVEL == "DEBUG" and settings.ENV == "dev" else None
		}
	)

# Exception handler untuk HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
	log_api(
		msg=f"HTTPException: {exc.status_code} - {exc.detail}",
		act="exception",
		level="ERROR"
	)
	return JSONResponse(
		status_code=exc.status_code,
		content={"message": exc.detail}
	)

# Exception handler untuk validasi request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	# error_detail = exc.errors()
	# error_messages = []
	
	# for error in error_detail:
	# 	error_messages.append({
	# 		"loc": error.get("loc", []),
	# 		"msg": error.get("msg", ""),
	# 		"type": error.get("type", "")
	# 	})
	
	# log_api(
	# 	msg=f"Validation error: {error_messages}",
	# 	act="exception",
	# 	level="ERROR"
	# )
	# if settings.LOG_LEVEL == "DEBUG" and settings.ENV == "dev":
	# 	return JSONResponse(
	# 		status_code=422,
	# 		content={
	# 			"message": "Validation Error",
	# 			"detail": error_messages,
	# 			"body": exc.body
	# 		}
	# 	)
	# else:
	# 	return JSONResponse(
	# 		status_code=422,
	# 		content={
	# 			"message": "Validation Error",
	# 			"detail": error_messages
	# 		}
	# 	)
	# errors: Dict[str, List[str]] = {}
	
	# for error in exc.errors():
	# 	# Extract location and field name
	# 	loc = error.get("loc", [])
	# 	field_path = []
		
	# 	for location in loc:
	# 		if location == "body":
	# 			continue
	# 		if isinstance(location, int):
	# 			field_path[-1] = f"{field_path[-1]}[{location}]"
	# 		else:
	# 			field_path.append(str(location))
		
	# 	field_name = ".".join(field_path) if field_path else "general"
		
	# 	# Format the error message
	# 	error_type = error.get("type", "")
	# 	error_msg = error.get("msg", "")
	# 	error_ctx = error.get("ctx")
		
	# 	formatted_msg = I18nErrorFormatter.format_errors(error, "en")
		
	# 	# Add to error dictionary
	# 	if field_name not in errors:
	# 		errors[field_name] = []
		
	# 	errors[field_name].append(formatted_msg)
	formatted_msg = I18nErrorFormatter.format_errors(exc, "en")
	
	ret = SingleErrorResponse(
		tx= getattr(request.state, "tx_id", None),
		req= getattr(request.state, "req_id", None),
		stat=False,
		msg="Validation failed",
		code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		err=formatted_msg
	)
	# Create a user-friendly response
	return JSONResponse(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		content=ret.model_dump()
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