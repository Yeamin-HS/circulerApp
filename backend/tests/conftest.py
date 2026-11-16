"""Every test runs against a fresh in-memory SQLite database (ADR-011)."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.auth import attempts
from app.db import models  # noqa: F401  (registers the tables)
from app.db.session import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def db() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)

    def override() -> Iterator[Session]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override
    attempts.hits.clear()
    with factory() as session:
        yield session
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def token(client: TestClient) -> str:
    """A registered seeker's access token."""
    body = {"email": "seeker@example.com", "password": "correct-horse-9"}
    return client.post("/auth/register", json=body).json()["access_token"]
