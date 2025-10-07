
from pydantic import BaseModel

from app.core.context import get_request_id, get_tx_id

class MessageResponse(BaseModel):
	message: str

class NoDataResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None

	def __init__(self, **data):
		if "tx" not in data or data["tx"] is None:
			data["tx"] = get_tx_id() or "-"
		
		if "req" not in data or data["req"] is None:
			data["req"] = get_request_id() or "-"
		
		super().__init__(**data)

class SingleDataResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None
	dt: dict | None = None

	def __init__(self, **data):
		if "tx" not in data or data["tx"] is None:
			data["tx"] = get_tx_id() or "-"
		
		if "req" not in data or data["req"] is None:
			data["req"] = get_request_id() or "-"
		
		super().__init__(**data)

class SingleErrorResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None
	err: dict | None = None

	def __init__(self, **data):
		if "tx" not in data or data["tx"] is None:
			data["tx"] = get_tx_id() or "-"
		
		if "req" not in data or data["req"] is None:
			data["req"] = get_request_id() or "-"
		
		super().__init__(**data)

class MultiDataResponse(BaseModel):
	tx: str | None = None
	req: str | None = None
	stat: bool = False
	msg: str = "NOK"
	code: int | None = None
	dtmap: dict[str, int] | None = None
	dt: list | None = None

	def __init__(self, **data):
		if "tx" not in data or data["tx"] is None:
			data["tx"] = get_tx_id() or "-"
		
		if "req" not in data or data["req"] is None:
			data["req"] = get_request_id() or "-"
		
		super().__init__(**data)