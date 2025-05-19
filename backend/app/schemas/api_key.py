import uuid
from datetime import datetime

from pydantic import BaseModel


class APIKeyBase(BaseModel):
    name: str
    expires_at: datetime | None = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyPublic(APIKeyBase):
    id: uuid.UUID
    key: str
    is_active: bool
    date_created: datetime

    class Config:
        from_attributes = True
