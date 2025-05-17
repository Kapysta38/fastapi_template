from secrets import token_urlsafe

from sqlalchemy.orm import Session
from app.models import APIKey
from app.schemas import APIKeyCreate
from app.crud.base import CRUDCreateOnly


class CRUDAPIKey(CRUDCreateOnly[APIKey, APIKeyCreate]):
    def __init__(self):
        super().__init__(APIKey)

    def create(self, db: Session, obj_in: APIKeyCreate) -> APIKey:
        key = token_urlsafe(32)
        db_key = self.model(name=obj_in.name, key=key, expires_at=obj_in.expires_at)
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        return db_key

    def get(self, db: Session, raw_key: str) -> APIKey | None:
        return db.query(self.model).filter(APIKey.key == raw_key, self.model.is_active.is_(True)).first()



api_crud = CRUDAPIKey()
