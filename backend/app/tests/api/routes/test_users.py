import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.crud import user_crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import User
from app.schemas import UserCreate
from app.tests.utils.utils import random_email, random_lower_string


def test_get_users_superuser_me(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data)
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = user_crud.get_by_email(db, email=username)
    assert user
    assert user.email == created_user["email"]


def test_get_existing_user(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user = user_crud.create(db, UserCreate(email=username, password=password))
    r = client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=superuser_token_headers)
    assert 200 <= r.status_code < 300
    api_user = r.json()
    assert api_user["email"] == username


def test_get_existing_user_permissions_error(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/{uuid.uuid4()}", headers=normal_user_token_headers)
    assert r.status_code == 403
    assert r.json()["detail"] == "Insufficient privileges"


def test_update_user_me(client: TestClient, normal_user_token_headers: dict[str, str], db: Session) -> None:
    full_name = "Updated Name"
    email = random_email()
    data = {"full_name": full_name, "email": email}
    r = client.patch(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers, json=data)
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["email"] == email
    assert updated_user["full_name"] == full_name

    user_db = db.scalars(select(User).where(User.email == email)).first()
    assert user_db
    assert user_db.full_name == full_name


def test_update_password_me(client: TestClient, superuser_token_headers: dict[str, str], db: Session) -> None:
    new_password = random_lower_string()
    data = {"current_password": settings.FIRST_SUPERUSER_PASSWORD, "new_password": new_password}
    r = client.patch(f"{settings.API_V1_STR}/users/me/password", headers=superuser_token_headers, json=data)
    assert r.status_code == 200
    assert r.json()["message"] == "Password updated successfully"

    user_db = db.scalars(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
    assert user_db and verify_password(new_password, user_db.hashed_password)

    # revert
    db.refresh(user_db)
    revert_data = {"current_password": new_password, "new_password": settings.FIRST_SUPERUSER_PASSWORD}
    r = client.patch(f"{settings.API_V1_STR}/users/me/password", headers=superuser_token_headers, json=revert_data)
    assert r.status_code == 200


def test_update_password_me_incorrect_password(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    new_password = random_lower_string()
    data = {"current_password": new_password, "new_password": new_password}
    r = client.patch(f"{settings.API_V1_STR}/users/me/password", headers=superuser_token_headers, json=data)
    assert r.status_code == 400
    assert r.json()["detail"] == "Incorrect current password"


def test_update_password_me_same_password_error(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    data = {"current_password": settings.FIRST_SUPERUSER_PASSWORD, "new_password": settings.FIRST_SUPERUSER_PASSWORD}
    r = client.patch(f"{settings.API_V1_STR}/users/me/password", headers=superuser_token_headers, json=data)
    assert r.status_code == 400
    assert r.json()["detail"] == "New password must differ"


def test_register_user(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": email, "password": password, "full_name": full_name}
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
    assert r.status_code == 200
    result = r.json()
    assert result["email"] == email

    user_db = db.scalars(select(User).where(User.email == email)).first()
    assert user_db and verify_password(password, user_db.hashed_password)


def test_register_user_already_exists_error(client: TestClient) -> None:
    data = {
        "email": settings.FIRST_SUPERUSER,
        "password": random_lower_string(),
        "full_name": random_lower_string(),
    }
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
    assert r.status_code == 400
    assert r.json()["detail"] == "User already exists."


def test_delete_user_me_as_superuser(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    r = client.delete(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    assert r.status_code == 403
    assert r.json()["detail"] == "Superusers cannot delete themselves"
