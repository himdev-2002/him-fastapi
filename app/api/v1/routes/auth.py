
"""
Authentication routes for the FastAPI application.

This module provides REST API endpoints for user authentication including login,
token refresh, and logout functionality. It handles JWT token generation,
validation, and session management using Redis for token whitelisting and blacklisting.

Endpoints:
    POST /auth/login - Authenticate user credentials and return JWT tokens
    POST /auth/refresh - Refresh access token using refresh token
    POST /auth/logout - Invalidate access token and log out user

Dependencies:
    - JWT token management via JWTSession
    - User authentication via user_service
    - Redis for token session management
    - FastAPI for HTTP handling

"""

import jwt
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_current_user
from app.middlewares.context import set_tx_id, reset_tx_id, set_route, reset_route
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, LogoutRequest
from app.services.login_manager_service import LoginManagerAuthService
from app.services.user_service import authenticate_user
from app.core.config import settings
from app.utils.logger import log_api
from app.utils.helpers import generate_tx_id, get_current_route
from app.core.auth_manager import manager
from app.models.user import User
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize authentication service
auth_service = LoginManagerAuthService(manager)


@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="Authenticate user and generate tokens",
    description="Authenticate user credentials and return JWT access and refresh tokens.",
    tags=["auth"],
    response_description="JWT tokens for authenticated user"
)
async def login(request: Request, data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user using form data and generate JWT tokens.
    
    Args:
        request (Request): FastAPI request object.
        data (OAuth2PasswordRequestForm): Form data containing username and password.
        
    Returns:
        TokenResponse: Access token, refresh token, and expiration info.
        
    Raises:
        HTTPException: If authentication fails or token generation fails.
    """
    tx_id = generate_tx_id(act="login")
    route = get_current_route(request)
    setattr(request.state, "user", data.username)
    setattr(request.state, "tx_id", tx_id)
    setattr(request.state, "act", "login")
    
    log_api(
        f"Login attempt for user: {data.username}", 
        user=data.username, 
        route=route['path'], 
        act="auth", 
        level="INFO", 
        tx_id=tx_id
    )
    
    tx_token = await set_tx_id(tx_id)
    route_token = await set_route(route['path'])
    
    # Authenticate user
    user = authenticate_user(data.username, data.password)
    log_api(
        f"Authentication result: {user is not None}", 
        route=route['path'], 
        user=data.username, 
        act="auth", 
        level="DEBUG", 
        tx_id=tx_id
    )
    
    if not user:
        await reset_tx_id(tx_token)
        await reset_route(route_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    # Create access token using LoginManager
    access_token = auth_service.create_access_token(user)
    if not access_token:
        await reset_tx_id(tx_token)
        await reset_route(route_token)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to generate access token"
        )
    
    # Create refresh token
    try:
        log_api(
            f"Decoding access token for refresh token creation", 
            route=route['path'], 
            user=str(user.id), 
            act="auth", 
            level="INFO", 
            tx_id=tx_id
        )
        access_payload = jwt.decode(access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        uniq_key = access_payload.get("_key")
        jti = access_payload.get("jti")
        log_api(
            f"Uniq key extracted: {uniq_key}", 
            route=route['path'], 
            user=str(user.id), 
            act="auth", 
            level="DEBUG", 
            tx_id=tx_id
        )
        
        refresh_token = auth_service.create_refresh_token(user.id, uniq_key=uniq_key, jti=jti)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60
        )
    except Exception as e:
        log_api(
            f"Failed to create refresh token: {e}", 
            route=route['path'], 
            user=str(user.id), 
            act="auth", 
            level="ERROR", 
            tx_id=tx_id
        )
        await reset_tx_id(tx_token)
        await reset_route(route_token)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to generate refresh token"
        )

@router.post(
    "/refresh", 
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token.",
    tags=["auth"],
    response_description="New access token and refresh token info"
)
async def refresh_token(request: Request, data: RefreshRequest, current_user: User = Depends(get_current_user)):
    """
    Refresh access token using refresh token.
    
    Args:
        request (RefreshRequest): Request containing refresh token.
        user: Current authenticated user from LoginManager.
        
    Returns:
        TokenResponse: New access token and refresh token info.
        
    Raises:
        HTTPException: If refresh token is invalid or expired.
    """
    tx_id = generate_tx_id(act="refresh_token")
    route = get_current_route(request)
    setattr(request.state, "user", current_user.username)
    setattr(request.state, "tx_id", tx_id)
    setattr(request.state, "act", "refresh_token")
    
    log_api(
        f"Refresh token attempt: {data.refresh_token}", 
        user=str(current_user.id), 
        route=route['path'], 
        act="auth", 
        level="INFO", 
        tx_id=tx_id
    )
    
    tx_token = await set_tx_id(tx_id)
    route_token = await set_route(route['path'])
    try:
        user_id1 = int(current_user.id)
        uniq_key1 = request.state.req_id
        jti1 = request.state.jti
        log_api(
            f"User ID: {user_id1} uniq_key: {uniq_key1} jti: {jti1}", 
            route=route['path'], 
            user=str(current_user.id), 
            act="auth", 
            level="DEBUG", 
            tx_id=tx_id
        )
        payload2 = jwt.decode(data.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
        user_id2 = int(payload2["sub"])
        uniq_key2 = payload2.get("_key")
        jti2 = payload2.get("jti")
        log_api(
            f"Comparing => User ID: {user_id1} uniq_key: {uniq_key1} jti: {jti1} | user_id2: {user_id2} uniq_key2: {uniq_key2} jti2: {jti2}", 
            route=route['path'], 
            user=str(current_user.id), 
            act="auth", 
            level="DEBUG", 
            tx_id=tx_id
        )
        if user_id1 != user_id2 or uniq_key1 != uniq_key2 or jti1 != jti2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
    except Exception as e:
        log_api(
            f"Invalid refresh token: {e}", 
            route=route['path'], 
            user=str(current_user.id), 
            act="auth", 
            level="ERROR", 
            tx_id=tx_id
        )
        await reset_tx_id(tx_token)
        await reset_route(route_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid refresh token", 
        )
    
    new_access_token, jti = auth_service.refresh_access_token(user_id1, uniq_key1, jti1)
    if not new_access_token:
        await reset_tx_id(tx_token)
        await reset_route(route_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token expired or invalid", 
        )
    
    refresh_token = auth_service.create_refresh_token(user_id1, uniq_key=uniq_key1, jti=jti)
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60, 
    )


@router.post(
    "/logout",
    summary="Logout user",
    description="Invalidate access token and log out the user.",
    tags=["auth"],
    response_description="Logout confirmation message"
)
async def logout(request: LogoutRequest, current_user: User = Depends(get_current_user)):
    """
    Logout user by blacklisting the access token.
    
    Args:
        request (LogoutRequest): Request containing access token to blacklist.
        
    Returns:
        dict: Logout confirmation message.
        
    Raises:
        HTTPException: If token is invalid.
    """
    try:
        payload = jwt.decode(request.access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload["sub"])
        uniq_key = payload.get("_key")
    except Exception as e:
        log_api(
            f"Invalid token during logout: {e}", 
            act="auth", 
            level="ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )
    
    auth_service.blacklist_token(request.access_token, user_id)
    
    log_api(
        f"User logged out successfully", 
        user=str(user_id), 
        act="auth", 
        level="INFO"
    )
    
    return {"msg": f"Logged out successfully (uniq_key={uniq_key})"}
