import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.item import create_random_item


def test_create_item(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content


def test_read_item(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(item.id)
    assert content["title"] == item.title
    assert content["description"] == item.description


def test_read_item_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"{settings.API_V1_STR}/items/{fake_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_read_items(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    create_random_item(db)
    create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content["data"], list)
    assert len(content["data"]) >= 2
    assert "count" in content


def test_update_item(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    item = create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(item.id)
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]


def test_update_item_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    fake_id = str(uuid.uuid4())
    response = client.put(
        f"{settings.API_V1_STR}/items/{fake_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_item(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    item = create_random_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


def test_delete_item_not_found(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    fake_id = str(uuid.uuid4())
    response = client.delete(
        f"{settings.API_V1_STR}/items/{fake_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
