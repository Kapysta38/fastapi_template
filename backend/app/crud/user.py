from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.crud.base import CRUDBaseFull


class CRUDUser(CRUDBaseFull[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(
            self, db: AsyncSession, email: str
    ) -> Optional[User]:
        stmt = (
            select(self.model)
            .where(self.model.email == email)
            .limit(1)
        )
        result = await db.scalars(stmt)
        return result.first()

    async def create(
            self, db: AsyncSession, obj_in: UserCreate
    ) -> User:
        db_obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            hashed_password=get_password_hash(obj_in.password),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
            self, db: AsyncSession, db_obj: User, obj_in: UserUpdate
    ) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
            self, db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_crud = CRUDUser()
