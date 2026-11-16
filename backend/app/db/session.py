"""Database engine and session (ADR-011)."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Neon scales to zero; a pooled connection may be dead
    connect_args={"check_same_thread": False} if _sqlite else {},
)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from app.db import models  # noqa: F401  (registers the tables)

    Base.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


Db = Annotated[Session, Depends(get_db)]
