"""Password hashing (argon2id) and JWT handling (ADR-001)."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings

ALGORITHM = "HS256"
_hasher = PasswordHasher()  # argon2id with the library's recommended parameters
# Verified when the email is unknown, so both failure paths take about the same time.
_DUMMY_HASH = _hasher.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def create_token(user_id: int, role: str) -> tuple[str, int]:
    """Return (token, seconds until it expires)."""
    seconds = settings.jwt_minutes * 60
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=seconds),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=ALGORITHM), seconds


def decode_token(token: str) -> int | None:
    """Return the user id, or None if the token is invalid or expired."""
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(claims["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
