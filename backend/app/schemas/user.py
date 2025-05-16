from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


# Базовая схема (общие поля)
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


# При создании (через API)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


# Регистрация (отдельная форма)
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = None


# При обновлении (всё необязательное)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


# Обновление текущего пользователя
class UserUpdateMe(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


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
