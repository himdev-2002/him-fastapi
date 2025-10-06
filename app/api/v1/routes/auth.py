
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

from turtle import st
import jwt
from fastapi import APIRouter, HTTPException, Response, status, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_current_user
from app.middlewares.context import generate_tx_id, set_tx_id, reset_tx_id, set_route, reset_route
from app.schemas.auth import LoginRequest, LogoutResponse, TokenResponse, RefreshRequest, LogoutRequest
from app.services.login_manager_service import LoginManagerAuthService
from app.services.user_service import authenticate_user
from app.core.config import settings
from app.utils.logger import log_api
from app.utils.helpers import end_route, get_current_route, init_route
from app.core.auth_manager import manager
from app.models.user import User
from app.schemas.response import NoDataResponse
router = APIRouter(prefix="/auth", tags=["auth"])

# Initialize authentication service
auth_service = LoginManagerAuthService(manager)


@router.post(
    "/login", 
    response_model=TokenResponse | NoDataResponse,
    summary="Authenticate user and generate tokens",
    description="Authenticate user credentials and return JWT access and refresh tokens.",
    tags=["auth"],
    response_description="JWT tokens for authenticated user"
)
async def login(response: Response, request: Request, data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user using form data and generate JWT tokens.
    
    Args:
        response (Response): FastAPI response object.
        request (Request): FastAPI request object.
        data (OAuth2PasswordRequestForm): Form data containing username and password.
        
    Returns:
        TokenResponse: Access token, refresh token, and expiration info.
        NoDataResponse: If authentication fails or token generation fails.
    """
    # Create refresh token
    msg = "OK"
    code = status.HTTP_200_OK
    access_token = None
    refresh_token = None
    tx_id, route, tx_token, route_token = await init_route(request, data.username, "auth", "login")
    log_api(
        f"Login attempt for user: {data.username}", 
        user=data.username, 
        route=route['path'], 
        act="auth", 
        level="INFO", 
        tx_id=tx_id
    )
    try:
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
            # await end_route(tx_token, route_token)
            code = status.HTTP_401_UNAUTHORIZED
            msg = "Invalid credentials"
            # return NoDataResponse(
            #     tx=tx_id,
            #     stat=False,
            #     msg="Invalid credentials"
            # )
            # raise HTTPException(
            #     status_code=status.HTTP_401_UNAUTHORIZED, 
            #     detail="Invalid credentials"
            # )
        else:
            # Create access token using LoginManager
            access_token = auth_service.create_access_token(user)
            if not access_token:
                code = status.HTTP_500_INTERNAL_SERVER_ERROR
                msg = "Failed to generate access token"
                # await end_route(tx_token, route_token)
                # raise HTTPException(
                #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                #     detail="Failed to generate access token"
                # )
            else:
                log_api(
                    f"Decoding access token for refresh token creation", 
                    route=route['path'], 
                    user=data.username, 
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
                    user=data.username, 
                    act="auth", 
                    level="DEBUG", 
                    tx_id=tx_id
                )
                
                refresh_token = auth_service.create_refresh_token(user.id, uniq_key=uniq_key, jti=jti)
                if not refresh_token:
                    code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    msg = "Failed to generate refresh token"
                    # await end_route(tx_token, route_token)
                    # raise HTTPException(
                    #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    #     detail="Failed to generate refresh token"
                    # )
    except Exception as e:
        log_api(
            f"Failed to authenticate user: {e}", 
            route=route['path'], 
            user=data.username, 
            act="auth", 
            level="ERROR", 
            tx_id=tx_id
        )
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = e.message
        # await end_route(tx_token, route_token)
        # raise HTTPException(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        #     detail="Failed to generate refresh token"
        # )

    await end_route(tx_token, route_token)
    if msg != "OK" or code != status.HTTP_200_OK:
        response.status_code = code
        return NoDataResponse(
            tx=tx_id,
            req=request.state.req_id,
            stat=False,
            msg=msg,
            code=code
        )
    else:
        log_api(
            f"Login successful", 
            user=data.username, 
            route=route['path'], 
            act="auth", 
            level="INFO", 
            tx_id=tx_id
        )
        response.status_code = code
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60
        )

@router.post(
    "/refresh", 
    response_model=TokenResponse | NoDataResponse,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token.",
    tags=["auth"],
    response_description="New access token and refresh token info"
)
async def refresh_token(response: Response, request: Request, data: RefreshRequest, current_user: User = Depends(get_current_user)):
    """
    Refresh access token using refresh token.
    
    Args:
        request (RefreshRequest): Request containing refresh token.
        user: Current authenticated user from LoginManager.
        
    Returns:
        TokenResponse: New access token and refresh token info.
        NoDataResponse: If refresh token is invalid or expired.
    """
    msg = "OK"
    code = status.HTTP_200_OK
    new_access_token = None
    refresh_token = None
    tx_id, route, tx_token, route_token = await init_route(request, current_user.username, "auth", "refresh_token")
    log_api(
        f"Refresh token attempt: {data.refresh_token}", 
        user=str(current_user.id), 
        route=route['path'], 
        act="auth", 
        level="INFO", 
        tx_id=tx_id
    )
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
            code = status.HTTP_401_UNAUTHORIZED
            msg = "Invalid refresh token"
        else:
            new_access_token, jti = auth_service.refresh_access_token(user_id1, uniq_key1, jti1)
            if not new_access_token:
                code = status.HTTP_401_UNAUTHORIZED
                msg = "Refresh token expired or invalid"
            else:
                refresh_token = auth_service.create_refresh_token(user_id1, uniq_key=uniq_key1, jti=jti)
                if not refresh_token:
                    code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    msg = "Failed to generate refresh token"
    except Exception as e:
        log_api(
            f"Failed to refresh token: {e}", 
            route=route['path'], 
            user=str(current_user.id), 
            act="auth", 
            level="ERROR", 
            tx_id=tx_id
        )
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = e.message

    await end_route(tx_token, route_token)
    if msg != "OK" or code != status.HTTP_200_OK:
        response.status_code = code
        return NoDataResponse(
            tx=tx_id,
            req=request.state.req_id,
            stat=False,
            msg=msg,
            code=code
        )
    else:
        log_api(
            f"Refresh token successful", 
            user=str(current_user.id), 
            route=route['path'], 
            act="auth", 
            level="INFO", 
            tx_id=tx_id
        )
        response.status_code = code
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60
        )

@router.post(
    "/logout",
    response_model=LogoutResponse | NoDataResponse,
    summary="Logout user",
    description="Invalidate access token and log out the user.",
    tags=["auth"],
    response_description="Logout confirmation message"
)
async def logout(response: Response, request: Request, current_user: User = Depends(get_current_user)):
    """
    Logout user by blacklisting the access token.
    
    Args:
        request (LogoutRequest): Request containing access token to blacklist.
        
    Returns:
        LogoutResponse: Logout confirmation message.
        NoDataResponse: If token is invalid.
    """
    msg = "OK"
    code = status.HTTP_200_OK
    tx_id, route, tx_token, route_token = await init_route(request, current_user.username, "auth", "logout")
    log_api(
        f"Logout attempt: {current_user.id}", 
        user=str(current_user.id), 
        route=route['path'], 
        act="auth", 
        level="INFO", 
        tx_id=tx_id
    )
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            code = status.HTTP_401_UNAUTHORIZED
            msg = "Invalid token"
        else:
            access_token = auth_header.split(" ", 1)[1]
            auth_service.blacklist_token(access_token, current_user.id)
    except Exception as e:
        log_api(
            f"Failed to logout: {e}", 
            route=route['path'], 
            user=str(current_user.id), 
            act="auth", 
            level="ERROR",
            tx_id=tx_id
        )
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = e.message
    

    await end_route(tx_token, route_token)
    if msg != "OK" or code != status.HTTP_200_OK:
        response.status_code = code
        return NoDataResponse(
            tx=tx_id,
            req=request.state.req_id,
            stat=False,
            msg=msg,
            code=code
        )
    else:
        log_api(
            f"Logout successful", 
            user=str(current_user.id), 
            route=route['path'], 
            act="auth", 
            level="INFO", 
            tx_id=tx_id
        )
        response.status_code = code
        return LogoutResponse(
            status=True,
            message="Logged out successfully"
        )
