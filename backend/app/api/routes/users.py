import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.security import get_password_hash, verify_password
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.common import Message
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> UsersPublic:
    """Return paginated list of users (superuser-only)."""
    count_result = await session.execute(select(func.count()).select_from(User))
    count: int = count_result.scalar_one()

    users = await user_crud.get_multi(session, skip=skip, limit=limit)
    return UsersPublic(data=users, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    status_code=201,
)
async def create_user(session: SessionDep, user_in: UserCreate) -> UserPublic:
    existing = await user_crud.get_by_email(session, user_in.email)
    if existing:
        raise HTTPException(
            status_code=400, detail="User with this email already exists."
        )
    user = await user_crud.create(session, user_in)
    return user


@router.post("/signup", response_model=UserPublic, status_code=201)
async def register_user(session: SessionDep, user_in: UserRegister) -> UserPublic:
    if await user_crud.get_by_email(session, user_in.email):
        raise HTTPException(status_code=400, detail="User already exists.")

    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    return await user_crud.create(session, user_create)


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> UserPublic:
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
) -> UserPublic:
    if user_in.email:
        existing = await user_crud.get_by_email(session, user_in.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already in use")

    return await user_crud.update(session, db_obj=current_user, obj_in=user_in)


@router.patch("/me/password", response_model=Message)
async def update_password_me(
    session: SessionDep,
    current_user: CurrentUser,
    body: UpdatePassword,
) -> Message:
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password must differ")

    current_user.hashed_password = get_password_hash(body.new_password)
    session.add(current_user)
    await session.commit()

    return Message(message="Password updated successfully")


@router.delete("/me", response_model=Message)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Message:
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Superusers cannot delete themselves"
        )

    await session.delete(current_user)
    await session.commit()
    return Message(message="User deleted successfully")


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> UserPublic:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> UserPublic:
    db_user = await user_crud.get(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email:
        existing = await user_crud.get_by_email(session, user_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=409, detail="Email already exists")

    return await user_crud.update(session, db_obj=db_user, obj_in=user_in)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
async def delete_user(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
) -> Message:
    user = await user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="You can't delete yourself")

    await session.delete(user)
    await session.commit()
    return Message(message="User deleted successfully")
