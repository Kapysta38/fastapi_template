from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_api_key_success(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    data = {"name": "test-key", "expires_at": "2025-05-19T16:06:54.012Z"}

    response = client.post(
        f"{settings.API_V1_STR}/api-keys/",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "key" in data
    assert data["name"] == data["name"]
    assert data["expires_at"] == data["expires_at"]
