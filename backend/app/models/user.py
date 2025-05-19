from sqlalchemy import Boolean, Column, String

from app.db.base import Base
from app.db.mixins import BaseModelMixin


class User(BaseModelMixin, Base):
    __tablename__ = "user"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
