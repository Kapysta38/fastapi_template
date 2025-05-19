import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.db.session import AsyncSessionLocal
from app.db.init_db import init_db
from app.models.user import User
from app.models.item import Item
from app.models.api_key import APIKey
from app.main import app
from app.core.config import settings
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        await init_db(session)
        yield session
        # Очистка после теста
        await session.execute(delete(Item))
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def api_key_header(db: AsyncSession) -> dict[str, str]:
    key_value = str(uuid.uuid4())
    api_key = APIKey(
        key=key_value,
        name="Test Key",
        expires_at=datetime.now() + timedelta(days=1),
    )
    db.add(api_key)
    await db.commit()
    return {"X-API-Key": key_value}


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as ac:
        yield ac



@pytest_asyncio.fixture(scope="function")
async def superuser_token_headers(client: AsyncClient) -> dict[str, str]:
    return await get_superuser_token_headers(client)


@pytest_asyncio.fixture(scope="function")
async def normal_user_token_headers(
    client: AsyncClient, db: AsyncSession
) -> dict[str, str]:
    return await authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )