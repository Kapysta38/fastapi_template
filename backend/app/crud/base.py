from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDOnlyRead(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> ModelType | None:
        return await session.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result: ScalarResult[ModelType] = await db.scalars(stmt)
        return result.all()


class CRUDCreateOnly(CRUDOnlyRead[ModelType], Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


class CRUDUpdateOnly(CRUDOnlyRead[ModelType], Generic[ModelType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)

    async def update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


class CRUDBaseFull(
    CRUDCreateOnly[ModelType, CreateSchemaType],
    CRUDUpdateOnly[ModelType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)

    async def remove(self, session: AsyncSession, id: Any) -> ModelType | None:
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj
