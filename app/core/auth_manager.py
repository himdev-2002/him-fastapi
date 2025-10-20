"""
Authentication manager configuration for FastAPI application.

This module contains the LoginManager configuration and user loader function
to avoid circular import issues.
"""

from fastapi_login import LoginManager
from app.core.config import settings
from app.models.user import User
from app.core.database import engine_sync
from sqlalchemy import select
from app.utils.database import map_to_pydantic
from app.schemas.user import UserLoginResponse
from app.utils.logger import log_api

# Configure LoginManager
manager = LoginManager(settings.JWT_SECRET, token_url="/api/v1/auth/login")

@manager.user_loader()
def load_user(id: str) -> User | None:
    """
    Load user by id for LoginManager authentication.
    
    Args:
        id (str): The id to load.
        
    Returns:
        User | None: User object if found, None otherwise.
    """
    try:
        # print(("LOAD USER", id))
        query = select(User).where(User.id == int(id))
        # print(("LOAD USER", query))
        # log_api(f"Loading user {id}", act="auth", level="INFO")
        with engine_sync.connect() as conn:
            result = conn.execute(query)
            res_data = result.first()
            if res_data:
                user = User(
                    id=res_data.id,
                    username=res_data.username,
                    email=res_data.email,
                    password=res_data.password,
                    is_active=res_data.is_active,
                    created_by=res_data.created_by,
                    created_at=res_data.created_at,
                    updated_by=res_data.updated_by,
                    updated_at=res_data.updated_at
                )
                return user
            return None
    except Exception as e:
        log_api(f"Error loading user {id}: {e}", act="auth", level="ERROR")
        return None
