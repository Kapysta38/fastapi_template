import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.api_key import APIKeyCreate
from app.core.config import settings


@pytest.mark.asyncio
async def test_create_api_key_success(
    client: AsyncClient,
    db: AsyncSession,
    superuser_token_headers: dict[str, str],
):
    data = {"name": "test-key", "expires_at": "2025-05-19T16:06:54.012Z"}

    response = await client.post(
        f"{settings.API_V1_STR}/api-keys/",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "key" in data
    assert data["name"] == data["name"]
    assert data["expires_at"] == data["expires_at"]
