from typing import Optional
from secrets import token_urlsafe

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import APIKey
from app.schemas import APIKeyCreate
from app.crud.base import CRUDCreateOnly


class CRUDAPIKey(CRUDCreateOnly[APIKey, APIKeyCreate]):
    def __init__(self):
        super().__init__(APIKey)

    async def create(
            self, session: AsyncSession, obj_in: APIKeyCreate
    ) -> APIKey:
        # генерируем 256-битный токен
        # TODO : hash token in DB
        key_plain = token_urlsafe(32)

        db_key = self.model(
            name=obj_in.name,
            key=key_plain,
            expires_at=obj_in.expires_at,
        )

        session.add(db_key)
        await session.commit()
        await session.refresh(db_key)
        return db_key

    async def get(
            self, session: AsyncSession, raw_key: str
    ) -> Optional[APIKey]:
        stmt = (
            select(self.model)
            .where(
                self.model.key == raw_key,
                self.model.is_active.is_(True),
            )
            .limit(1)
        )
        result = await session.scalars(stmt)
        return result.first()


api_crud = CRUDAPIKey()
