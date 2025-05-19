import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app.api.deps import SessionDep, get_api_key_record
from app.crud.item import item_crud
from app.models.item import Item
from app.schemas.common import Message
from app.schemas.item import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/",
    dependencies=[Depends(get_api_key_record)],
    response_model=ItemsPublic,
)
async def read_items(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> ItemsPublic:
    """
    Retrieve all items (paginated).
    """
    # Кол-во записей
    count_result = await session.execute(select(func.count()).select_from(Item))
    count: int = count_result.scalar_one()

    # Сами записи
    items = await item_crud.get_multi(session, skip=skip, limit=limit)

    return ItemsPublic(data=items, count=count)


@router.get(
    "/{id}",
    dependencies=[Depends(get_api_key_record)],
    response_model=ItemPublic,
)
async def read_item(session: SessionDep, id: uuid.UUID) -> ItemPublic:
    """
    Get item by ID.
    """
    item = await item_crud.get(session, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post(
    "/",
    dependencies=[Depends(get_api_key_record)],
    response_model=ItemPublic,
    status_code=201,
)
async def create_item(
    session: SessionDep,
    item_in: ItemCreate,
) -> ItemPublic:
    """
    Create new item.
    """
    return await item_crud.create(session, item_in)


@router.put(
    "/{id}",
    dependencies=[Depends(get_api_key_record)],
    response_model=ItemPublic,
)
async def update_item(
    session: SessionDep,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> ItemPublic:
    """
    Update item by ID.
    """
    item = await item_crud.get(session, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return await item_crud.update(session, db_obj=item, obj_in=item_in)


@router.delete(
    "/{id}",
    dependencies=[Depends(get_api_key_record)],
    response_model=Message,
)
async def delete_item(
    session: SessionDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete item by ID.
    """
    item = await item_crud.get(session, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await item_crud.remove(session, id)
    return Message(message="Item deleted successfully")
