from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    return {"Authorization": f"Bearer {response['access_token']}"}


async def create_random_user(db: AsyncSession) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    return await user_crud.create(db, user_in)


async def authentication_token_from_email(
    *, client: TestClient, email: str, db: AsyncSession
) -> dict[str, str]:
    password = random_lower_string()
    user = await user_crud.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        _ = await user_crud.create(db, user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        _ = await user_crud.update(db, user, user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
