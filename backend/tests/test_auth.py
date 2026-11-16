from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import settings
from app.core.errors import ApiError
from app.core.security import ALGORITHM, create_token, hash_password, verify_password
from app.db.models import User

CREDENTIALS = {"email": "seeker@example.com", "password": "correct-horse-9"}


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_creates_a_seeker_and_signs_in(client: TestClient, db: Session) -> None:
    response = client.post("/auth/register", json=CREDENTIALS)
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer" and body["expires_in"] == 3600

    me = client.get("/me", headers=auth(body["access_token"]))
    assert me.status_code == 200
    assert me.json()["email"] == "seeker@example.com"
    assert me.json()["role"] == "seeker"
    assert me.json()["consent_at"] is None
    assert me.json()["has_confirmed_profile"] is False

    stored = db.scalar(select(User))
    assert stored.password_hash.startswith("$argon2id$")
    assert CREDENTIALS["password"] not in stored.password_hash


def test_register_rejects_a_duplicate_email_in_any_case(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENTIALS)
    again = client.post("/auth/register", json=CREDENTIALS | {"email": "Seeker@Example.com"})
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "email_taken"


def test_register_rejects_a_short_password(client: TestClient) -> None:
    response = client.post("/auth/register", json=CREDENTIALS | {"password": "short"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_login_returns_a_working_token(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENTIALS)
    response = client.post("/auth/login", json=CREDENTIALS | {"email": "SEEKER@example.com"})
    assert response.status_code == 200
    assert client.get("/me", headers=auth(response.json()["access_token"])).status_code == 200


def test_login_fails_the_same_way_for_wrong_password_and_unknown_email(client: TestClient) -> None:
    client.post("/auth/register", json=CREDENTIALS)
    wrong = client.post("/auth/login", json=CREDENTIALS | {"password": "wrong-password"})
    unknown = client.post("/auth/login", json=CREDENTIALS | {"email": "nobody@example.com"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert wrong.json()["error"]["code"] == "invalid_credentials"


def test_bad_tokens_are_rejected(client: TestClient, token: str) -> None:
    now = datetime.now(UTC)
    expired = jwt.encode(
        {"sub": "1", "exp": now - timedelta(minutes=1)}, settings.jwt_secret, ALGORITHM
    )
    forged = jwt.encode({"sub": "1", "exp": now + timedelta(hours=1)}, "x" * 48, ALGORITHM)
    unsigned = jwt.encode({"sub": "1", "exp": now + timedelta(hours=1)}, "", algorithm="none")
    for bad in (expired, forged, unsigned, token + "x", "not-a-token"):
        response = client.get("/me", headers=auth(bad))
        assert response.status_code == 401, bad
        assert response.json()["error"]["code"] == "unauthorized"


def test_token_stops_working_when_the_account_is_gone(
    client: TestClient, token: str, db: Session
) -> None:
    db.delete(db.scalar(select(User)))
    db.commit()
    assert client.get("/me", headers=auth(token)).status_code == 401


def test_role_guard_allows_admins_only(db: Session) -> None:
    seeker = User(email="s@example.com", password_hash="x", role="seeker")
    admin = User(email="a@example.com", password_hash="x", role="admin")
    assert require_admin(admin) is admin
    with pytest.raises(ApiError) as raised:
        require_admin(seeker)
    assert (raised.value.status, raised.value.code) == (403, "forbidden")


def test_role_comes_from_the_database_not_the_token(client: TestClient, db: Session) -> None:
    """A token that claims admin does not make a seeker an admin."""
    client.post("/auth/register", json=CREDENTIALS)
    user = db.scalar(select(User))
    claimed_admin, _ = create_token(user.id, "admin")
    assert client.get("/me", headers=auth(claimed_admin)).json()["role"] == "seeker"


def test_login_is_rate_limited_per_ip(client: TestClient) -> None:
    for _ in range(10):
        assert client.post("/auth/login", json=CREDENTIALS).status_code == 401
    blocked = client.post("/auth/login", json=CREDENTIALS)
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
    assert blocked.json()["error"]["retry_after"] > 0
    assert int(blocked.headers["Retry-After"]) > 0


def test_password_hashing_round_trip() -> None:
    hashed = hash_password("correct-horse-9")
    assert verify_password("correct-horse-9", hashed)
    assert not verify_password("wrong", hashed)
    assert not verify_password("correct-horse-9", None)
    assert not verify_password("correct-horse-9", "not-a-hash")
