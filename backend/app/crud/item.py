from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBaseFull
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBaseFull[Item, ItemCreate, ItemUpdate]):
    def __init__(self):
        super().__init__(Item)

    async def get_by_title(self, session: AsyncSession, title: str) -> Sequence[Item]:
        stmt = select(self.model).where(
            self.model.title == title,
        )
        result = await session.execute(stmt)
        return result.scalars().all()


item_crud = CRUDItem()
