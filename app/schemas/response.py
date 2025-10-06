
from pydantic import BaseModel

class MessageResponse(BaseModel):
	message: str

class NoDataResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None

class SingleDataResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None
	dt: dict | None = None

class MultiDataResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None
	dtmap: dict[str, int] | None = None
	dt: list | None = None