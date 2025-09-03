
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
	name: str
	email: EmailStr

class UserCreate(UserBase):
	password: str

class UserUpdate(UserBase):
	pass

class UserResponse(UserBase):
	id: int

	model_config = ConfigDict(from_attributes=True)
