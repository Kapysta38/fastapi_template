from sqlmodel import Session

from app.crud import item_crud
from app.models import Item
from app.schemas import ItemCreate
from app.tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return item_crud.create(db, obj_in=item_in)
