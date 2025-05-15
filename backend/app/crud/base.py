from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDOnlyRead(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).get(id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()


class CRUDCreateOnly(CRUDOnlyRead[ModelType], Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model(**obj_in.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj


class CRUDUpdateOnly(CRUDOnlyRead[ModelType], Generic[ModelType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDBaseFull(CRUDCreateOnly[ModelType, CreateSchemaType], CRUDUpdateOnly[ModelType, UpdateSchemaType],
                   Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)

    def remove(self, db: Session, id: Any) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
