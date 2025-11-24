import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
import fastapi.openapi.utils as fau
from app.api.v1 import api_router
from app.schemas.response import SingleErrorResponse
from app.handler.exception import glob_except_handler, http_except_handler, validate_except_handler
from app.core.config import settings
from app.utils.logger import log_api
from app.core import database
from app.core.redis_client import test_redis_connection
from app.utils.helpers import is_awaitable
from app.core.limiter import configure_limiter
from app.middlewares import setup_middlewares

class Core():
    app: FastAPI | None = None

    def __init__(self):
        pass # do nothing

    def extend_fastapi(self):
        log_api(
            msg=f"Override FastAPI schema...",
            act="app",
            level="INFO"
        )
        # override the schema
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

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Run DB and Redis connectivity checks at application startup. Fail startup if tests fail."""
        log_api(msg="Running startup connectivity checks...", act="app", level="INFO")
        
        # Test Redis connection in a thread (avoid blocking event loop)
        try:
            ok_redis = await asyncio.get_event_loop().run_in_executor(None, test_redis_connection)
            if ok_redis is not None:
                raise Exception(f"Redis connection test returned False: {ok_redis}")
            log_api(msg="Redis connection OK", act="app", level="INFO")
        except Exception as exc:
            log_api(msg=f"Redis connection failed: {exc}", act="app", level="CRITICAL")
            raise

        # Test sync connection in a thread (avoid blocking event loop)
        try:
            ok_sync = await asyncio.get_event_loop().run_in_executor(None, database.test_sync_connection)
            if not ok_sync:
                raise Exception("Sync DB test returned False")
            log_api(msg="Sync DB connection OK", act="app", level="INFO")
        except Exception as exc:
            log_api(msg=f"Sync DB connection failed: {exc}", act="app", level="CRITICAL")
            raise

        # Test async connection directly
        try:
            ok_async = await database.test_async_connection()
            if not ok_async:
                raise Exception("Async DB test returned False")
            log_api(msg="Async DB connection OK", act="app", level="INFO")
        except Exception as exc:
            log_api(msg=f"Async DB connection failed: {exc}", act="app", level="CRITICAL")
            raise
        yield
        # Dispose of database engines properly
        if is_awaitable(database.engine_sync.dispose):
            await database.engine_sync.dispose()
        else:
            database.engine_sync.dispose()
        
        if is_awaitable(database.engine_async.dispose):
            await database.engine_async.dispose()
        else:
            database.engine_async.dispose()
        
        if is_awaitable(database.engine_txonly.dispose):
            await database.engine_txonly.dispose()
        else:
            database.engine_txonly.dispose()
        
        if is_awaitable(database.engine_txonly_async.dispose):
            await database.engine_txonly_async.dispose()
        else:
            database.engine_txonly_async.dispose()
        
        log_api(msg="Application shutdown", act="app", level="INFO")

 
    def init_handlers(self):
        # Exception handler untuk semua exception
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            return await glob_except_handler(request, exc)

        
        # Exception handler untuk HTTPException
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return await http_except_handler(request, exc)

            
        # Exception handler untuk validasi request
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return await validate_except_handler(request, exc)


    def init_middlewares(self):
        setup_middlewares(self.app)

    def init_routes(self):
        log_api(
            msg="Starting Configure API Endpoints...",
            act="app",
            level="INFO"
        )
        self.app.include_router(api_router)


    def init_app(self):
        log_api(
            msg=f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} application...",
            act="app",
            level="INFO"
        )
        if self.app is None:
            self.app = FastAPI(
                title=settings.APP_NAME,
                version=settings.APP_VERSION,
                docs_url=settings.SWAGGER_URL,
                redoc_url=settings.REDOC_URL,
                lifespan=self.lifespan,
            )
            self.extend_fastapi()
            configure_limiter(self.app)
            self.init_handlers()
            self.init_middlewares()
            self.init_routes()

        log_api(
            msg=f"Done initializing {settings.APP_NAME} v{settings.APP_VERSION} application.",
            act="app",
            level="INFO"
        )

        return self.app

        