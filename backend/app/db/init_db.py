from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_crud
from app.schemas import UserCreate
from app.core.config import settings

from app.models import *  # Импортируй модели, чтобы Base "знал" их

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