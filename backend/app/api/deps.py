"""Shared route dependencies. The real token check arrives in Story 2.1 (ADR-001)."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ApiError, not_implemented
from app.core.schemas import ErrorResponse

bearer = HTTPBearer(auto_error=False, description="JWT from /auth/login, valid 60 minutes")


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> None:
    if credentials is None:
        raise ApiError(401, "unauthorized", "Missing bearer token.")
    raise not_implemented("2.1")


CurrentUser = Annotated[None, Depends(current_user)]

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
