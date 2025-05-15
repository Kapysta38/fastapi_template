import uuid
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

class BaseModelMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = Column(DateTime, nullable=False, default=func.now())
    date_updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
