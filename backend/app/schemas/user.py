from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    id: UUID
    email: str
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True
