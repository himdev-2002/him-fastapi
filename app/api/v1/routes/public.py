from json.encoder import JSONEncoder
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, ValidationError
from app.utils.logger import log_api
from app.schemas.public import HashResponse, HashRequest, IPInfoResponse, JSONHashResponse, JSONIPInfoResponse, JSONVerifyResponse,VerifyResponse, VerifyRequest
from app.schemas.response import NoDataResponse
from app.utils.helpers import init_route, end_route, verify_password
from app.utils.client import client_ip_dependency
from app.core.config import settings
from app.core.limiter import limiter

try:
    # prefer passlib if installed
    from passlib.hash import bcrypt
    def make_bcrypt(pw: str) -> str:
        return bcrypt.hash(pw)
except Exception:
    import bcrypt as _bcrypt
    def make_bcrypt(pw: str) -> str:
        return _bcrypt.hashpw(pw.encode('utf-8'), _bcrypt.gensalt()).decode()

router = APIRouter(prefix="/public", tags=["public"])

@router.post(
    "/bcrypt", 
    response_model=JSONHashResponse | NoDataResponse,
    summary="Generate bcrypt hash",
    description="Generate bcrypt hash",
    tags=["public"],
    response_description="New access token and refresh token info"
)
@limiter.limit(settings.RATE_LIMIT_LOW)
async def gen_bcrypt(response: Response, request: Request, payload: HashRequest):
    msg = "OK"
    code = status.HTTP_200_OK
    h = None
    tx_id, route, tx_token, route_token = await init_route(request, "public", "public", "gen_bcrypt")
    log_api(
        f"Generate bcrypt hash: {payload.password}", 
        user="public", 
        route=route['path'], 
        act="public", 
        level="DEBUG", 
        tx_id=tx_id
    )

    try:
        _data = HashRequest.model_validate(payload)
        h = make_bcrypt(_data.password)
        log_api(msg="Generated password bcrypt hash", user="public", route=route['path'], act="public", level="DEBUG", tx_id=tx_id)
    except ValidationError as e:
        log_api(f"Validation ssss sass error: {e}",  user="public", route=route['path'], act="public", level="ERROR", tx_id=tx_id)
        code = status.HTTP_400_BAD_REQUEST
        msg = e.message
    except Exception as e:
        log_api(f"Failed to generate bcrypt hash: {e}", user="public", route=route['path'], act="public", level="ERROR", tx_id=tx_id)
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
            f"Generate bcrypt hash successful", 
            user="public", 
            route=route['path'], 
            act="public", 
            level="INFO", 
            tx_id=tx_id
        )
        response.status_code = code
        return JSONHashResponse(
            tx=tx_id,
            req=request.state.req_id,
            stat=True,
            msg=msg,
            code=code,
            dt=HashResponse(hash=h)
        ) 

@router.post("/bcrypt/verify", 
    response_model=JSONVerifyResponse | NoDataResponse,
    summary="Verify bcrypt hash",
    description="Verify bcrypt hash",
    tags=["public"],
    response_description="Verify password result"
)
async def verify_bcrypt(response: Response, request: Request, payload: VerifyRequest):
    msg = "OK"
    code = status.HTTP_200_OK
    tx_id, route, tx_token, route_token = await init_route(request, "public", "public", "verify_bcrypt")
    log_api(
        f"Verify bcrypt hash: {payload.password} {payload.hash} {payload.valid}", 
        user="public", 
        route=route['path'], 
        act="public", 
        level="DEBUG", 
        tx_id=tx_id
    )
    
    try:
        _data = VerifyRequest.model_validate(payload)
        valid = verify_password(_data.password, _data.hash)
        log_api(msg=f"Verify password result={valid}", act="public", level="DEBUG", tx_id=tx_id)
    except Exception as e:
        log_api(f"Failed to verify bcrypt hash: {e}", act="public", level="ERROR", tx_id=tx_id)
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
        return JSONVerifyResponse(
            tx=tx_id,
            req=request.state.req_id,
            stat=True,
            msg=msg,
            code=code,
            dt=VerifyResponse(valid=valid)
        )
        
@router.get("/ip-info",
    response_model=JSONIPInfoResponse | NoDataResponse,
    summary="Get IP info",
    description="Get IP info",
    tags=["public"],
    response_description="IP info"
)
async def get_ip_info(response: Response, request: Request, client_ip_info: [str, str] = Depends(client_ip_dependency)):
    msg = "OK"
    code = status.HTTP_200_OK
    tx_id, route, tx_token, route_token = await init_route(request, "public", "public", "get_ip_info")
    log_api(
        f"Get IP info: {client_ip_info}",
        user=client_ip_info[0],
        route=route['path'],
        act="public",
        level="DEBUG",
        tx_id=tx_id
    )
    
    return JSONIPInfoResponse(
        tx=tx_id,
        req=request.state.req_id,
        stat=True,
        msg=msg,
        code=code,
        dt=IPInfoResponse(client_ip=client_ip_info[0], client_ip_type=client_ip_info[1])
    )