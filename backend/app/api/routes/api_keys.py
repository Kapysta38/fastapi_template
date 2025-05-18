
from fastapi import APIRouter, Depends
from app.schemas.api_key import APIKeyCreate, APIKeyPublic
from app.api.deps import SessionDep, get_current_active_superuser
from app.crud import api_crud

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=APIKeyPublic)
async def create_api_key(
    session: SessionDep,
    api_key_in: APIKeyCreate
):
    return await api_crud.create(session, api_key_in)
