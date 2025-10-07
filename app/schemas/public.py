
from pydantic import BaseModel
from app.schemas.response import SingleDataResponse


class HashRequest(BaseModel):
    password: str


class HashResponse(BaseModel):
    hash: str
    
class VerifyRequest(BaseModel):
    password: str
    hash: str

class VerifyResponse(BaseModel):
    valid: bool

class IPInfoResponse(BaseModel):
    client_ip: str
    client_ip_type: str

class JSONHashResponse(SingleDataResponse):
    dt: HashResponse | None = None

class JSONVerifyResponse(SingleDataResponse):
    dt: VerifyResponse | None = None

class JSONIPInfoResponse(SingleDataResponse):
    dt: IPInfoResponse | None = None