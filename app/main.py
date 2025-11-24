import asyncio
import sys
from app.core.main import Core

if sys.platform.startswith("win"):
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app =Core().init_app()