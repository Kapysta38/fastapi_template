import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app.api.deps import SessionDep, CurrentUser, get_current_active_superuser
from app.core.security import get_password_hash, verify_password
from app.schemas import (
    UserCreate,
    UserRegister,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
    Message
)
from app.crud import user_crud
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=UsersPublic)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> UsersPublic:
    count = session.execute(select(func.count()).select_from(User)).scalar()
    users = user_crud.get_multi(session, skip=skip, limit=limit)
    return UsersPublic(data=users, count=count)


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def create_user(session: SessionDep, user_in: UserCreate) -> UserPublic:
    existing = user_crud.get_by_email(session, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    user = user_crud.create(session, user_in)

    return user


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> UserPublic:
    existing = user_crud.get_by_email(session, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists.")
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    return user_crud.create(session, user_create)


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> UserPublic:
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(session: SessionDep, current_user: CurrentUser, user_in: UserUpdateMe) -> UserPublic:
    if user_in.email:
        existing = user_crud.get_by_email(session, user_in.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=409, detail="Email already in use")

    return user_crud.update(session, db_obj=current_user, obj_in=user_in)


@router.patch("/me/password", response_model=Message)
def update_password_me(session: SessionDep, current_user: CurrentUser, body: UpdatePassword) -> Message:
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password must differ")

    current_user.hashed_password = get_password_hash(body.new_password)
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Message:
    if current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superusers cannot delete themselves")
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> UserPublic:
    user = user_crud.get(session, user_id)
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def update_user(session: SessionDep, user_id: uuid.UUID, user_in: UserUpdate) -> UserPublic:
    db_user = user_crud.get(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email:
        existing = user_crud.get_by_email(session, user_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=409, detail="Email already exists")

    return user_crud.update(session, db_obj=db_user, obj_in=user_in)


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Message)
def delete_user(session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID) -> Message:
    user = user_crud.get(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="You can't delete yourself")
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
