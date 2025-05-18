from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.crud.base import CRUDBaseFull


class CRUDItem(CRUDBaseFull[Item, ItemCreate, ItemUpdate]):
    def __init__(self):
        super().__init__(Item)

    async def get_by_title(self, session: AsyncSession, title: str) -> Sequence[Item]:
        stmt = (
            select(self.model)
            .where(
                self.model.title == title,
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()


item_crud = CRUDItem()
