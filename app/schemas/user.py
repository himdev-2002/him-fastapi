
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.response import SingleDataResponse, MultiDataResponse
from app.utils.helpers import extend_example

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

class PublicFullUserResponse(FullUserResponse):
	# Override password field to exclude it
	password: Optional[str] = Field(None, exclude=True)
	created_by: Optional[int] = Field(None, exclude=True)
	updated_by: Optional[int] = Field(None, exclude=True)
	updated_at: Optional[datetime] = Field(None, exclude=True)

class JsonUserResponse(SingleDataResponse):
	dt: UserResponse | None = None

class JsonMultiUserResponse(MultiDataResponse):
	dtmap: dict[str, int] | None = Field(None, example={
		"id": 0,
		"username": 1,
		"email": 2,
		"is_active": 3,
		"created_at": 4,
		"updated_at": 5,
	})
	dt: list[list[Any]] | None = Field(None)
	
	model_config = ConfigDict(
		json_schema_extra = {
			"example": {
				"tx": "get_users-abc123def456-7890",
				"req": "req-xyz789uvw012-3456",
				"stat": True,
				"msg": "OK",
				"code": 600200,
				"dtmap": {
					"created_at": 0,
					"email": 1,
					"id": 2,
					"is_active": 3,
					"username": 4
				},
				"dt": [
					["2025-09-13T01:53:50.486793","staff@mail.com",4,True,"staff"],
    				["2025-09-13T01:53:50.486000","him@mail.com",2,True,"him"]
				],
            }
		}
	)

class JsonFullUserResponse(SingleDataResponse):
	dt: PublicFullUserResponse | None = None