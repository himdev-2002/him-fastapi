"""
Dependencies for FastAPI application.

This module provides reusable dependencies for authentication, database access,
and other common functionality across the application.
"""

from fastapi import Depends, HTTPException, status

from app.core.auth_manager import manager
from app.models.user import User
from app.utils.logger import log_api


def get_current_user(user=Depends(manager)) -> User:
    """
    Get the current authenticated user.
    
    This dependency uses LoginManager to authenticate the user from the JWT token
    in the Authorization header.
    
    Args:
        user: The authenticated user from LoginManager.
        
    Returns:
        User: The authenticated user object.
        
    Raises:
        HTTPException: If user is not authenticated or token is invalid.
    """
    if not user:
        log_api("Authentication failed: No user found", act="auth", level="WARNING")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    elif type(user) == User:
        log_api(f"User authenticated: {user.username}", user=str(user.id), act="auth", level="DEBUG")
        return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    This dependency extends get_current_user to ensure the user is active.
    Currently, all users are considered active, but this can be extended
    to check for user status flags.
    
    Args:
        current_user (User): The current authenticated user.
        
    Returns:
        User: The current active user.
        
    Raises:
        HTTPException: If user is not active.
    """
    # TODO: Add user active status check when user model is extended
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Inactive user"
    #     )
    
    return current_user


def get_current_user_optional(user=Depends(manager)) -> User | None:
    """
    Get the current user if authenticated, otherwise return None.
    
    This dependency is useful for endpoints that work for both authenticated
    and unauthenticated users.
    
    Args:
        user: The user from LoginManager (can be None if not authenticated).
        
    Returns:
        User | None: The authenticated user or None.
    """
    return user if user else None
