from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Базовая схема (общие поля)
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


# При создании (через API)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


# Регистрация (отдельная форма)
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = None


# При обновлении (всё необязательное)
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=40)
    full_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


# Обновление текущего пользователя
class UserUpdateMe(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


# Обновление пароля
class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Публичная схема
class UserPublic(UserBase):
    id: UUID

    class Config:
        from_attributes = True


# Ответ на список пользователей
class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int

    class Config:
        from_attributes = True
