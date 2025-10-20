from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.schemas.profile import JSONProfileResponse
from app.schemas.response import NoDataResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.core.constants import RES_CODE
from app.utils.logger import log_api
from app.core.config import settings
from app.core.limiter import limiter
from app.services.profile import ProfileService

ACT = "profile"
router = APIRouter(prefix="/profile", tags=[ACT])

@router.get("s/", 
    response_model=JSONProfileResponse | NoDataResponse,
    summary="Get profiles",
    description="Get profiles",
    tags=["master"],
    name="get_profiles",
    response_description="Profiles"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_profile(response: Response, request: Request, current_user: User = Depends(get_current_user)):
    msg,rid,code,rescode = "OK",200,RES_CODE.PROFILE,status.HTTP_200_OK
    profiles = []

    log_api(f"Getting list of profiles", level="DEBUG")

    try:
        profile_service = ProfileService()
        profiles, msg = profile_service.get_profiles()
        if msg:
            code = code+rid+1
            msg = msg
            rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
            log_api(f"Failed to get list of profiles [{code}]: {msg}", level="ERROR")
        else:
            code = code+RES_CODE.OK_CODE+rid
            log_api(f"List of profiles found [{code}]", level="INFO")
    except Exception as e:
        code = code+rid
        rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = e.message
        log_api(f"Failed to get list of profiles [{code}]: {e}", level="ERROR")

    response.status_code = rescode
    if msg != "OK" or code < RES_CODE.OK_CODE:
        return NoDataResponse(
            stat=False,
            msg=msg,
            code=code
        )
    else:
        return JSONProfileResponse(
            stat=True,
            msg=msg,
            code=code,
            dt=profiles
        )