
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
	username: str
	email: EmailStr
	is_active: bool | None

class UserCreate(UserBase):
	password: str

class UserUpdate(UserBase):
	pass

class UserResponse(UserBase):
	id: int

	model_config = ConfigDict(from_attributes=True)

class UserLoginResponse(UserCreate):
	id: int

	model_config = ConfigDict(from_attributes=True)

class FullUserResponse(UserCreate):
	id: int
	created_by: int
	created_at: datetime
	updated_by: int
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
