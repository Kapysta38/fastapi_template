from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User


async def test_create_user(client: AsyncClient, db: AsyncSession) -> None:
    payload = {
        "email": "pollo@listo.com",
        "password": "password123",
        "full_name": "Pollo Listo",
    }

    response = await client.post(
        f"{settings.API_V1_STR}/private/users/", json=payload
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]

    result = await db.execute(select(User).where(User.id == data["id"]))
    user_in_db = result.scalar_one_or_none()
    assert user_in_db is not None
    assert user_in_db.email == payload["email"]
    assert user_in_db.full_name == payload["full_name"]