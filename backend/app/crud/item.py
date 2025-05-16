from sqlalchemy.orm import Session
from app.models import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.crud.base import CRUDBaseFull


class CRUDItem(CRUDBaseFull[Item, ItemCreate, ItemUpdate]):
    def __init__(self):
        super().__init__(Item)

    def get_by_title(self, db: Session, title: str) -> list[Item]:
        return db.query(self.model).filter(self.model.title == title).all()


item_crud = CRUDItem()
