import uuid
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.tests.utils.item import create_random_item


async def test_create_item(client: AsyncClient, api_key_header: dict[str, str]) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = await client.post(
        f"{settings.API_V1_STR}/items/",
        headers=api_key_header,
        json=data,
    )
    assert response.status_code == 201, response.text
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content


async def test_read_item(
    client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = await client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(item.id)
    assert content["title"] == item.title
    assert content["description"] == item.description


async def test_read_item_not_found(
    client: AsyncClient, api_key_header: dict[str, str]
) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.get(
        f"{settings.API_V1_STR}/items/{fake_id}",
        headers=api_key_header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


async def test_read_items(
    client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession
) -> None:
    await create_random_item(db)
    await create_random_item(db)
    response = await client.get(
        f"{settings.API_V1_STR}/items/",
        headers=api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content["data"], list)
    assert len(content["data"]) >= 2
    assert "count" in content


async def test_update_item(
    client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = await client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=api_key_header,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(item.id)
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]


async def test_update_item_not_found(
    client: AsyncClient, api_key_header: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    fake_id = str(uuid.uuid4())
    response = await client.put(
        f"{settings.API_V1_STR}/items/{fake_id}",
        headers=api_key_header,
        json=data,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


async def test_delete_item(
    client: AsyncClient, api_key_header: dict[str, str], db: AsyncSession
) -> None:
    item = await create_random_item(db)
    response = await client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=api_key_header,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


async def test_delete_item_not_found(
    client: AsyncClient, api_key_header: dict[str, str]
) -> None:
    fake_id = str(uuid.uuid4())
    response = await client.delete(
        f"{settings.API_V1_STR}/items/{fake_id}",
        headers=api_key_header,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
