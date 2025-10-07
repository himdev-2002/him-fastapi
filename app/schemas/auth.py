
from pydantic import BaseModel

class LoginRequest(BaseModel):
	username: str
	password: str

class RefreshRequest(BaseModel):
	refresh_token: str

class LogoutRequest(BaseModel):
	access_token: str

class TokenBlacklist(BaseModel):
	token: str
	expires_at: int

class LogoutResponse(BaseModel):
	status: bool
	message: str

class TokenResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"
	expires_in: int