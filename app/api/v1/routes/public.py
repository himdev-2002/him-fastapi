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
from app.core.constants import RES_CODE

try:
	# prefer passlib if installed
	from passlib.hash import bcrypt
	def make_bcrypt(pw: str) -> str:
		return bcrypt.hash(pw)
except Exception:
	import bcrypt as _bcrypt
	def make_bcrypt(pw: str) -> str:
		return _bcrypt.hashpw(pw.encode('utf-8'), _bcrypt.gensalt()).decode()

ACT = "public"
router = APIRouter(prefix="/public", tags=[ACT])

@router.post(
	"/bcrypt", 
	response_model=JSONHashResponse | NoDataResponse,
	summary="Generate bcrypt hash",
	description="Generate bcrypt hash",
	tags=["encryption"],
	name="gen_bcrypt",
	response_description="New access token and refresh token info"
)
@limiter.limit(settings.RATE_LIMIT_LOW)
async def gen_bcrypt(response: Response, request: Request, payload: HashRequest):
	msg,rid,code,rescode = "OK",100,RES_CODE.PUBLIC,status.HTTP_200_OK
	h = None

	# _, _, tx_token, route_token = await init_route(request, "guest", ACT, "gen_bcrypt")
	log_api(f"Generate bcrypt hash: {payload.password}", level="DEBUG")

	try:
		_data = HashRequest.model_validate(payload)
		h = make_bcrypt(_data.password)
		code = code+RES_CODE.OK_CODE+rid
		log_api(msg=f"Successfully generated bcrypt hash [{code}]", user="public", level="INFO")
	except ValidationError as e:
		code = code+rid+1
		rescode = status.HTTP_400_BAD_REQUEST
		msg = e.message
		log_api(f"Validation error [{code}]: {e}",  user="public", level="ERROR")
	except Exception as e:
		code = code+rid
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		msg = e.message
		log_api(f"Failed to generate bcrypt hash [{code}]: {e}", user="public", level="ERROR")

	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JSONHashResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=HashResponse(hash=h)
		) 

@router.post("/bcrypt/verify", 
	response_model=JSONVerifyResponse | NoDataResponse,
	summary="Verify bcrypt hash",
	description="Verify bcrypt hash",
	tags=["encryption"],
	name="verify_bcrypt",
	response_description="Verify password result"
)
@limiter.limit(settings.RATE_LIMIT_LOW)
async def verify_bcrypt(response: Response, request: Request, payload: VerifyRequest):
	msg,rid,code,rescode = "OK",200,RES_CODE.PUBLIC,status.HTTP_200_OK
	valid = False

	log_api(f"Verify bcrypt hash: {payload.password} {payload.hash}", act=ACT, level="DEBUG")

	try:
		_data = VerifyRequest.model_validate(payload)
		valid = verify_password(_data.password, _data.hash)
		code = code+RES_CODE.OK_CODE+rid
		log_api(msg=f"Verify password result [{code}]: {valid}", act=ACT, level="INFO")
	except ValidationError as e:
		code = code+rid+1
		rescode = status.HTTP_400_BAD_REQUEST
		msg = e.message
		log_api(f"Validation error [{code}]: {e}", act=ACT, level="ERROR")
	except Exception as e:
		code = code+rid
		rescode = status.HTTP_500_INTERNAL_SERVER_ERROR
		msg = e.message
		log_api(f"Failed to verify bcrypt hash [{code}]: {e}", act=ACT, level="ERROR")

	response.status_code = rescode
	if msg != "OK" or code < RES_CODE.OK_CODE:
		return NoDataResponse(
			stat=False,
			msg=msg,
			code=code
		)
	else:
		return JSONVerifyResponse(
			stat=True,
			msg=msg,
			code=code,
			dt=VerifyResponse(valid=valid)
		)
		
@router.get("/ip-info",
	response_model=JSONIPInfoResponse | NoDataResponse,
	summary="Get IP info",
	description="Get IP info",
	tags=["client"],
	name="get_ip_info",
	response_description="IP info"
)
@limiter.limit(settings.RATE_LIMIT_LOW)
async def get_ip_info(response: Response, request: Request, client_ip_info: [str, str] = Depends(client_ip_dependency)):
	msg,rid,code,rescode = "OK",300,RES_CODE.PUBLIC,status.HTTP_200_OK
	ip_info = None

	code = code+RES_CODE.OK_CODE+rid
	log_api(f"Get IP info [{code}]: {client_ip_info}", act=ACT, level="DEBUG")
	response.status_code = rescode
	return JSONIPInfoResponse(
		stat=True,
		msg=msg,
		code=code,
		dt=IPInfoResponse(client_ip=client_ip_info[0], client_ip_type=client_ip_info[1])
	)