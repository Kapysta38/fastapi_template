import uuid

from pydantic import BaseModel, Field


# Базовые свойства
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Создание
class ItemCreate(ItemBase):
    pass


# Обновление
class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Ответ через API
class ItemPublic(ItemBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class ItemsPublic(BaseModel):
    data: list[ItemPublic]
    count: int

    class Config:
        from_attributes = True
