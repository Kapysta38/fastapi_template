from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_active_superuser
from app.crud.api_key import api_crud
from app.schemas.api_key import APIKeyCreate, APIKeyPublic

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=APIKeyPublic,
)
async def create_api_key(session: SessionDep, api_key_in: APIKeyCreate) -> APIKeyPublic:
    api_key = await api_crud.create(session, api_key_in)
    return APIKeyPublic.model_validate(api_key)
