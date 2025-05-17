import uuid

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func

from app.api.deps import SessionDep, get_api_key_record
from app.models import Item
from app.crud import item_crud
from app.schemas.item import ItemsPublic, ItemPublic, ItemUpdate, ItemCreate
from app.schemas.common import Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/",  dependencies=[Depends(get_api_key_record)], response_model=ItemsPublic)
def read_items(
        db: SessionDep,
        skip: int = 0,
        limit: int = 100,
) -> ItemsPublic:
    """
    Retrieve all items.
    """
    count = db.execute(select(func.count()).select_from(Item)).scalar()
    items = item_crud.get_multi(db, skip=skip, limit=limit)
    return ItemsPublic(data=items, count=count)


@router.get("/{id}", dependencies=[Depends(get_api_key_record)], response_model=ItemPublic)
def read_item(db: SessionDep, id: uuid.UUID) -> Item:
    """
    Get item by ID.
    """
    item = item_crud.get(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", dependencies=[Depends(get_api_key_record)], response_model=ItemPublic)
def create_item(
        db: SessionDep,
        item_in: ItemCreate,
) -> Item:
    """
    Create new item.
    """
    return item_crud.create(db, item_in)


@router.put("/{id}", dependencies=[Depends(get_api_key_record)], response_model=ItemPublic)
def update_item(
        db: SessionDep,
        id: uuid.UUID,
        item_in: ItemUpdate,
) -> Item:
    """
    Update item by ID.
    """
    item = item_crud.get(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_crud.update(db, db_obj=item, obj_in=item_in)


@router.delete("/{id}", dependencies=[Depends(get_api_key_record)], response_model=Message)
def delete_item(
        db: SessionDep,
        id: uuid.UUID,
) -> Message:
    """
    Delete item by ID.
    """
    item = item_crud.get(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item_crud.remove(db, id)
    return Message(message="Item deleted successfully")
