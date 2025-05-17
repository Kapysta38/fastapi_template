from sqlalchemy import Column, String, Boolean, DateTime

from app.db.base import Base
from app.db.mixins import BaseModelMixin


class APIKey(BaseModelMixin, Base):
    __tablename__ = "api_keys"

    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
