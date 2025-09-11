
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
	username: str
	email: EmailStr

class UserCreate(UserBase):
	password: str

class UserUpdate(UserBase):
	pass

class UserResponse(UserBase):
	id: int

	model_config = ConfigDict(from_attributes=True)

class FullUserResponse(UserBase):
	id: int
	password: str

	model_config = ConfigDict(from_attributes=True)
