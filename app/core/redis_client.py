import redis
import os
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    # db=settings.REDIS_DB,
    decode_responses=True,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD
)

REDIS_KEY_PREFIX = settings.APP_NAME.replace(" ", "_").lower()

def test_redis_connection(timeout: int = 5) -> str:
    """
    Test Redis connection and return True if successful, False otherwise.
    
    Returns:
        bool: True if Redis connection is successful, False otherwise.
    """
    try:
        # Test connection with ping
        resp = redis_client.ping()
        print(f"Ping response: {resp}")
        return None
    except redis.ConnectionError as e:
        return e.message
    except redis.AuthenticationError as e:
        return e.message
    except Exception as e:
        return e.message
