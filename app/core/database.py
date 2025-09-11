from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import asyncio

# Read DB urls from settings
SQLALCHEMY_DATABASE_URL = settings.DB_URL
SQLALCHEMY_DATABASE_URL_ASYNC = getattr(settings, "DB_URL_ASYNC", settings.DB_URL)

# Engines and session factories (sync + async)
engine_sync = create_engine(
	SQLALCHEMY_DATABASE_URL,
	echo= getattr(settings, "LOG_LEVEL", "INFO") == "DEBUG",
	future=True,
	connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
)
engine_async = create_async_engine(
	SQLALCHEMY_DATABASE_URL_ASYNC,
	echo= getattr(settings, "LOG_LEVEL", "INFO") == "DEBUG",
	future=True,
	connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL_ASYNC else {},
)

DBSessionSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)
DBSessionAsync = async_sessionmaker(
	autocommit=False, autoflush=False, bind=engine_async, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


def get_db():
	"""Dependency that yields a sync DB session."""
	db = DBSessionSync()
	try:
		yield db
	finally:
		db.close()


async def get_db_async():
	"""Dependency that yields an async DB session."""
	async with DBSessionAsync() as session:
		yield session


def test_sync_connection(timeout: int = 5) -> bool:
	"""
	Quick synchronous health check: try to acquire a connection and run a trivial query.
	Returns True on success, raises the underlying exception on failure.
	"""
	with engine_sync.connect() as conn:
		# small timeout guard using asyncio's loop (sync path still benefits)
		result = conn.execute(text("SELECT 1"))
		# fetchone() is available on result
		row = result.fetchone()
		return row is not None


async def test_async_connection(timeout: int = 5) -> bool:
	"""
	Quick asynchronous health check: open async connection and run a trivial query.
	Returns True on success, raises the underlying exception on failure.
	"""
	async with engine_async.connect() as conn:
		result = await conn.execute(text("SELECT 1"))
		row = result.fetchone()
		return row is not None


def test_async_connection_sync(timeout: int = 5) -> bool:
	"""
	Helper to run the async test from sync code (uses asyncio.run internally).
	"""
	try:
		return asyncio.run(test_async_connection(timeout=timeout))
	except Exception:
		# allow caller to handle/log exception
		raise