
from datetime import datetime
from pydantic import BaseModel
from app.schemas.response import MultiDataResponse

class ProfileResponse(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool
    created_by: int
    created_at: datetime
    updated_by: int
    updated_at: datetime

class JSONProfileResponse(MultiDataResponse):
    dt: list[ProfileResponse] | None = None