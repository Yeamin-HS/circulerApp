"""Register and login (Story 2.1, ADR-001)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import INVALID
from app.core.errors import ApiError
from app.core.ratelimit import RateLimit
from app.core.schemas import ErrorResponse, LoginRequest, RegisterRequest, TokenResponse
from app.core.security import create_token, hash_password, verify_password
from app.db.models import User
from app.db.session import Db

router = APIRouter(prefix="/auth", tags=["auth"], responses=INVALID)
# 10 attempts per 5 minutes per IP, shared by both routes: slows password guessing.
attempts = RateLimit(limit=10, window=300)
Limited = Annotated[None, Depends(attempts)]
TOO_MANY = {429: {"model": ErrorResponse}}


def _token(user: User) -> TokenResponse:
    token, seconds = create_token(user.id, user.role)
    return TokenResponse(access_token=token, expires_in=seconds)


@router.post(
    "/register",
    status_code=201,
    response_model=TokenResponse,
    responses={409: {"model": ErrorResponse}} | TOO_MANY,
)
def register(body: RegisterRequest, db: Db, _: Limited) -> TokenResponse:
    """Create a seeker account and sign in."""
    user = User(email=body.email.lower(), password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ApiError(409, "email_taken", "An account with this email already exists.") from exc
    return _token(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}} | TOO_MANY,
)
def login(body: LoginRequest, db: Db, _: Limited) -> TokenResponse:
    """Exchange email and password for a 60-minute JWT."""
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    # One message for both cases, so the reply does not reveal which emails have accounts.
    if not verify_password(body.password, user.password_hash if user else None):
        raise ApiError(401, "invalid_credentials", "Wrong email or password.")
    return _token(user)
