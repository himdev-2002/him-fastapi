
import logging
from datetime import datetime
from app.core.config import settings


logger = logging.getLogger(settings.APP_NAME)
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

def log_api(
    msg: str,
    request_id: str = None,
    user: str = None,
    route: str = None,
    level: str = "INFO"
):
    log_time = datetime.utcnow().isoformat()
    user_info = user or "anonymous"
    route_info = route or "-"
    req_id = request_id or "-"
    log_msg = (
        f"time={log_time} | req_id={req_id} | level={level} | user={user_info} | route={route_info} | msg=\"{msg}\""
    )
    if level == "ERROR":
        logger.error(log_msg)
    elif level == "WARNING":
        logger.warning(log_msg)
    elif level == "DEBUG":
        logger.debug(log_msg)
    else:
        logger.info(log_msg)
