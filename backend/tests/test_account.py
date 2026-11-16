from fastapi.testclient import TestClient
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table, func, select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import Base

CREDENTIALS = {"email": "seeker@example.com", "password": "correct-horse-9"}


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_consent_is_recorded_once(client: TestClient, token: str) -> None:
    assert client.get("/me", headers=auth(token)).json()["consent_at"] is None

    first = client.post("/me/consent", json={"accepted": True}, headers=auth(token))
    assert first.status_code == 200
    stamp = first.json()["consent_at"]
    assert stamp is not None

    again = client.post("/me/consent", json={"accepted": True}, headers=auth(token))
    assert again.json()["consent_at"] == stamp
    assert client.get("/me", headers=auth(token)).json()["consent_at"] == stamp


def test_consent_must_be_an_explicit_yes(client: TestClient, token: str) -> None:
    for body in ({"accepted": False}, {}, {"accepted": "yes"}):
        response = client.post("/me/consent", json=body, headers=auth(token))
        assert response.status_code == 422, body
    assert client.get("/me", headers=auth(token)).json()["consent_at"] is None


def test_profile_writes_are_closed_until_consent(client: TestClient, token: str) -> None:
    profile = {"full_name": "Test Seeker"}
    calls = [
        ("PUT", "/me/profile", {"json": profile}),
        ("POST", "/me/cv", {"files": {"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")}}),
    ]
    for method, path, kwargs in calls:
        response = client.request(method, path, headers=auth(token), **kwargs)
        assert response.status_code == 403, (method, path)
        assert response.json()["error"]["code"] == "consent_required"

    client.post("/me/consent", json={"accepted": True}, headers=auth(token))
    for method, path, kwargs in calls:  # open now, though still stubs until Story 2.3
        response = client.request(method, path, headers=auth(token), **kwargs)
        assert response.json()["error"]["code"] == "not_implemented", (method, path)


def test_delete_removes_the_account(client: TestClient, token: str, db: Session) -> None:
    assert client.delete("/me", headers=auth(token)).status_code == 204
    assert db.scalar(select(func.count()).select_from(User)) == 0
    assert client.get("/me", headers=auth(token)).status_code == 401
    assert client.post("/auth/login", json=CREDENTIALS).status_code == 401
    assert client.post("/auth/register", json=CREDENTIALS).status_code == 201  # email is free


def test_delete_only_touches_the_caller(client: TestClient, token: str, db: Session) -> None:
    other = {"email": "other@example.com", "password": "correct-horse-9"}
    other_token = client.post("/auth/register", json=other).json()["access_token"]
    client.delete("/me", headers=auth(token))
    assert client.get("/me", headers=auth(other_token)).json()["email"] == "other@example.com"


def test_delete_cascades_to_rows_that_belong_to_the_user(
    client: TestClient, token: str, db: Session
) -> None:
    """Stand-in for the profile, circular and log tables that arrive later."""
    owned = Table(
        "owned_rows",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey(User.id, ondelete="CASCADE")),
    )
    owned.create(db.get_bind())
    other = {"email": "other@example.com", "password": "correct-horse-9"}
    client.post("/auth/register", json=other)
    mine, theirs = db.scalars(select(User.id).order_by(User.id)).all()
    db.execute(owned.insert(), [{"user_id": mine}, {"user_id": mine}, {"user_id": theirs}])
    db.commit()

    client.delete("/me", headers=auth(token))
    assert db.scalars(select(owned.c.user_id)).all() == [theirs]


def test_every_table_that_points_at_users_cascades() -> None:
    """Guard for later stories: a new table with user data must use owner_fk()."""
    for table in Base.metadata.tables.values():
        for key in table.foreign_keys:
            if key.column.table.name == "users":
                assert key.ondelete == "CASCADE", f"{table.name}.{key.parent.name}"
