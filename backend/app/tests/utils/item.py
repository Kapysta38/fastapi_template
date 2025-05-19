from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.item import item_crud
from app.models.item import Item
from app.schemas.item import ItemCreate
from app.tests.utils.utils import random_lower_string


async def create_random_item(db: AsyncSession) -> Item:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return await item_crud.create(db, obj_in=item_in)
