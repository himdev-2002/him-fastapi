
from pydantic import BaseModel


class HashRequest(BaseModel):
    password: str


class HashResponse(BaseModel):
    hash: str
    
class VerifyRequest(BaseModel):
    password: str
    hash: str


class VerifyResponse(BaseModel):
    valid: bool

