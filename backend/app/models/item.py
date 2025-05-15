from sqlalchemy import Column, String

from app.db.base import Base
from app.db.mixins import BaseModelMixin


class Item(Base, BaseModelMixin):
    __tablename__ = "item"

    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Item(id={self.id}, title={self.title})>"