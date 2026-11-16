"""Tables (ARCHITECTURE §3). Only `users` exists so far; the rest arrive with their stories."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


def owner_fk(*, primary_key: bool = False) -> Mapped[int]:
    """Column that ties a row to its user. Every table holding user data must use this, so
    that deleting the account removes the rows (SOP hard rule 6). A test enforces it."""
    return mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=primary_key, index=True
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)  # stored lower-case
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="seeker")
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
