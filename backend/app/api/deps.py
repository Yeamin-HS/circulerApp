"""Shared route dependencies: the signed-in user and the role guard (ADR-001)."""

from datetime import UTC
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ApiError
from app.core.schemas import ErrorResponse, UserOut
from app.core.security import decode_token
from app.db.models import User
from app.db.session import Db

bearer = HTTPBearer(auto_error=False, description="JWT from /auth/login, valid 60 minutes")


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)], db: Db
) -> User:
    """The user behind the bearer token. Loaded from the database on every request, so a
    deleted account or a changed role takes effect at once, not when the token expires."""
    if credentials is None:
        raise ApiError(401, "unauthorized", "Missing bearer token.")
    user_id = decode_token(credentials.credentials)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise ApiError(401, "unauthorized", "Invalid or expired token.")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise ApiError(403, "forbidden", "Admin role required.")
    return user


AdminUser = Annotated[User, Depends(require_admin)]


def user_out(user: User) -> UserOut:
    def utc(moment):
        return moment.replace(tzinfo=UTC) if moment and moment.tzinfo is None else moment

    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        consent_at=utc(user.consent_at),
        has_confirmed_profile=False,  # profiles arrive in Story 2.3
        created_at=utc(user.created_at),
    )


# Documented error responses, reused by the routers.
INVALID = {422: {"model": ErrorResponse}}
AUTH_ERRORS = {401: {"model": ErrorResponse}} | INVALID
NOT_FOUND = {404: {"model": ErrorResponse}}
UPLOAD_ERRORS = {
    413: {"model": ErrorResponse},
    415: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    429: {"model": ErrorResponse},
}
