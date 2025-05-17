import pytest
import uuid
from datetime import datetime, timedelta
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import delete
from starlette.testclient import TestClient

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.models import User, Item, APIKey
from app.main import app
from app.core.config import settings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        init_db(db)
        yield db
    finally:
        db.execute(delete(Item))
        db.execute(delete(User))
        db.commit()
        db.close()


@pytest.fixture(scope="module")
def api_key_header(db: SessionLocal) -> dict[str, str]:
    key_value = str(uuid.uuid4())
    api_key = APIKey(
        key=key_value,
        name="Test Key",
        expires_at=datetime.now() + timedelta(days=1),
    )
    db.add(api_key)
    db.commit()
    return {"X-API-Key": key_value}


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
