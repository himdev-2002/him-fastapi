import logging as loging
import os
import colorlog
from logging.handlers import TimedRotatingFileHandler
# from datetime import datetime
from app.core.config import settings

# Buat folder logs kalau belum ada
os.makedirs("logs", exist_ok=True)

RESET = "\033[0m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
WHITE = "\033[37m"

# Custom filter supaya hanya log level tertentu yang masuk
class LevelFilter(loging.Filter):
    def __init__(self, level):
        self._level = level
    def filter(self, record):
        return record.levelno == self._level

# Filter berdasarkan custom act
class ActFilter(loging.Filter):
    def __init__(self, act):
        self.act = act
    def filter(self, record):
        # print(getattr(record, "act", None), self.act, record.levelno)
        return getattr(record, "act", None) == self.act and record.levelno != loging.DEBUG

# Formatter untuk console (berwarna)
console_formatter = colorlog.ColoredFormatter(
    # "%(log_color)s%(asctime)s %(levelname)s|%(req_id)s|%(pid)s|%(user)s|%(route)s|%(act)s|%(tx_id)s%(reset)s : %(message)s",
    f"%(white)s%(asctime)s%(reset)s %(log_color)s%(levelname)s%(reset)s|%(req_id)s|%(green)s%(pid)s%(reset)s|%(user)s|%(yellow)s%(route)s%(reset)s|%(cyan)s%(act)s%(reset)s|%(bold_red)s%(tx_id)s%(reset)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%MS",
    log_colors={
        "DEBUG": "white",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red,bg_white",
    }
)

# Formatter untuk file (tanpa warna)
file_formatter = loging.Formatter(
    "%(asctime)s %(levelname)s|%(req_id)s|%(pid)s|%(user)s|%(route)s|%(act)s|%(tx_id)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%MS"
)

def create_act_handler(filename, act, when="H", interval=1, backup_count=7):
    handler = TimedRotatingFileHandler(
        filename,
        # maxBytes=max_bytes,
        when=when,       # "S" detik, "M" menit, "H" jam, "D" hari, "midnight"
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
        utc=False
    )
    # handler.suffix = "%Y-%m-%d.log"
    # handler.extMatch = r"^\d{4}-\d{2}-\d{2}.log$"
    handler.setFormatter(file_formatter)
    handler.addFilter(ActFilter(act))
    return handler

act_config = {
    "logs/init_app.log": "init_app",
    "logs/auth.log": "auth",
    "logs/user.log": "user",
    "logs/debug.log": "debug",
    "logs/info.log": "info",
    "logs/warning.log": "warning",
    "logs/error.log": "error",
    "logs/critical.log": "critical",
}

# Handler Console (berwarna)
console_handler = loging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Handler File (plain text)
# file_handler = loging.FileHandler("logs/app.log", encoding="utf-8")
# file_handler.setFormatter(file_formatter)

# Setup logger
logger = loging.getLogger(settings.APP_NAME)
logger.setLevel(getattr(loging, settings.LOG_LEVEL.upper(), loging.INFO))
logger.addHandler(console_handler)
# logger.addHandler(file_handler)

# Tambahkan handler sesuai mapping
for file, act in act_config.items():
    handler = create_act_handler(file, act, backup_count=30)
    logger.addHandler(handler)


# console = loging.StreamHandler()
# console.setLevel(getattr(loging, settings.LOG_LEVEL.upper(), loging.INFO))
# formatter = loging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
# console.setFormatter(formatter)
# logger.addHandler(console)

def log_api(
    msg: str,
    user: str = None,
    route: str = None,
    level: str = "INFO",
    act: str = "DEBUG",
    tx_id: str = None
):
    # Import here to avoid circular import
    from app.middlewares.context import get_request_id
    
    # log_time = datetime.utcnow().isoformat()
    user_info = user or "-"
    route_info = route or "-"
    req_id = get_request_id() or "-"
    tx_info = tx_id or "-"
    process_id = os.getpid()
    log_msg = (
        f"{msg}"
    )
    # loging.debug(log_msg)
    
    if level == "CRITICAL":
        logger.critical(log_msg, extra={"req_id": req_id, "user": user_info, "route": route_info, "act": act, "tx_id": tx_info, "pid": process_id})
    elif level == "ERROR":
        logger.error(log_msg, extra={"req_id": req_id, "user": user_info, "route": route_info, "act": act, "tx_id": tx_info, "pid": process_id})
    elif level == "WARNING":
        logger.warning(log_msg, extra={"req_id": req_id, "user": user_info, "route": route_info, "act": act, "tx_id": tx_info, "pid": process_id})
    elif level == "INFO":
        logger.info(log_msg, extra={"req_id": req_id, "user": user_info, "route": route_info, "act": act, "tx_id": tx_info, "pid": process_id})
    else:
        logger.debug(log_msg, extra={"req_id": req_id, "user": user_info, "route": route_info, "act": act, "tx_id": tx_info, "pid": process_id})
