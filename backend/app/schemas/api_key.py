import uuid

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class APIKeyBase(BaseModel):
    name: str
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyPublic(APIKeyBase):
    id: uuid.UUID
    key: str
    is_active: bool
    date_created: datetime

    class Config:
        from_attributes = True
