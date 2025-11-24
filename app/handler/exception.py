
import traceback
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.constants import RES_CODE
from app.core.error import I18nErrorFormatter
from app.schemas.response import SingleErrorResponse
from app.utils.logger import log_api


async def glob_except_handler(request: Request, exc: Exception):
	error_traceback = traceback.format_exc()
	log_api(
		msg=f"Unhandled exception: {str(exc)}",
		act="error",
		level="ERROR"
	)
	
	return JSONResponse(
		status_code=500,
		content={
			"code": RES_CODE.SYSTEM+1,
			"message": "Internal Server Error",
			"detail": str(exc),
			"traceback": error_traceback.split("\n") if settings.LOG_LEVEL == "DEBUG" and settings.ENV == "dev" else None
		}
	)


async def http_except_handler(request: Request, exc: HTTPException):
	log_api(
		msg=f"HTTPException: {exc.status_code} - {exc.detail}",
		act="error",
		level="ERROR"
	)
	return JSONResponse(
		status_code=exc.status_code,
		content={"code": RES_CODE.SYSTEM+RES_CODE.HTTP+1, "message": exc.detail}
	)


async def validate_except_handler(request: Request, exc: RequestValidationError):
	# error_detail = exc.errors()
	# error_messages = []
	
	# for error in error_detail:
	# 	error_messages.append({
	# 		"loc": error.get("loc", []),
	# 		"msg": error.get("msg", ""),
	# 		"type": error.get("type", "")
	# 	})
	
	# log_api(
	# 	msg=f"Validation error: {error_messages}",
	# 	act="exception",
	# 	level="ERROR"
	# )
	# if settings.LOG_LEVEL == "DEBUG" and settings.ENV == "dev":
	# 	return JSONResponse(
	# 		status_code=422,
	# 		content={
	# 			"message": "Validation Error",
	# 			"detail": error_messages,
	# 			"body": exc.body
	# 		}
	# 	)
	# else:
	# 	return JSONResponse(
	# 		status_code=422,
	# 		content={
	# 			"message": "Validation Error",
	# 			"detail": error_messages
	# 		}
	# 	)
	# errors: Dict[str, List[str]] = {}
	
	# for error in exc.errors():
	# 	# Extract location and field name
	# 	loc = error.get("loc", [])
	# 	field_path = []
		
	# 	for location in loc:
	# 		if location == "body":
	# 			continue
	# 		if isinstance(location, int):
	# 			field_path[-1] = f"{field_path[-1]}[{location}]"
	# 		else:
	# 			field_path.append(str(location))
		
	# 	field_name = ".".join(field_path) if field_path else "general"
		
	# 	# Format the error message
	# 	error_type = error.get("type", "")
	# 	error_msg = error.get("msg", "")
	# 	error_ctx = error.get("ctx")
		
	# 	formatted_msg = I18nErrorFormatter.format_errors(error, "en")
		
	# 	# Add to error dictionary
	# 	if field_name not in errors:
	# 		errors[field_name] = []
		
	# 	errors[field_name].append(formatted_msg)
	formatted_msg = I18nErrorFormatter.format_errors(exc, "en")
	# print(request.state.__dict__)
	ret = SingleErrorResponse(
		tx= getattr(request.state, "tx_id", None),
		req= getattr(request.state, "req_id", None),
		stat=False,
		msg="Validation failed",
		code=RES_CODE.SYSTEM+RES_CODE.VALIDATION+1,
		err=formatted_msg
	)
	# Create a user-friendly response
	return JSONResponse(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		content=ret.model_dump()
	)