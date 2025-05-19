from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import user_crud
from app.schemas.user import UserCreate


async def init_db(session: AsyncSession) -> None:
    # Проверяем, есть ли суперпользователь
    superuser = await user_crud.get_by_email(session, email=settings.FIRST_SUPERUSER)
    if not superuser:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
            full_name="Superuser",
        )
        await user_crud.create(session, user_in)
