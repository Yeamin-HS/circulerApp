"""Auth routes (contract only; built in Story 2.1)."""

from fastapi import APIRouter

from app.api.deps import INVALID
from app.core.errors import not_implemented
from app.core.schemas import ErrorResponse, LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"], responses=INVALID)


@router.post(
    "/register",
    status_code=201,
    response_model=TokenResponse,
    responses={409: {"model": ErrorResponse}},
)
def register(body: RegisterRequest) -> TokenResponse:
    """Create a seeker account and sign in."""
    raise not_implemented("2.1")


@router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def login(body: LoginRequest) -> TokenResponse:
    """Exchange email and password for a 60-minute JWT."""
    raise not_implemented("2.1")
