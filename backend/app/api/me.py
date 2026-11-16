"""Account and profile routes (contract only; built in Stories 2.1-2.3)."""

from fastapi import APIRouter, UploadFile

from app.api.deps import AUTH_ERRORS, NOT_FOUND, UPLOAD_ERRORS, CurrentUser
from app.core.errors import not_implemented
from app.core.schemas import ConsentRequest, CVDraft, CVProfile, ErrorResponse, ProfileOut, UserOut

router = APIRouter(prefix="/me", tags=["me"], responses=AUTH_ERRORS)
CONSENT = {403: {"model": ErrorResponse}}


@router.get("", response_model=UserOut)
def get_me(user: CurrentUser) -> UserOut:
    """The signed-in user, with consent and profile state."""
    raise not_implemented("2.1")


@router.delete("", status_code=204)
def delete_me(user: CurrentUser) -> None:
    """Delete the account and all of its data. Cannot be undone."""
    raise not_implemented("2.2")


@router.post("/consent", response_model=UserOut)
def give_consent(body: ConsentRequest, user: CurrentUser) -> UserOut:
    """Record consent to store a profile. Required before /me/cv and /me/profile."""
    raise not_implemented("2.2")


@router.post("/cv", response_model=CVDraft, responses=UPLOAD_ERRORS | CONSENT)
def upload_cv(file: UploadFile, user: CurrentUser) -> CVDraft:
    """Upload a CV (PDF or DOCX, at most 5 MB) and get a draft profile. Nothing is saved."""
    raise not_implemented("2.3")


@router.put("/profile", response_model=ProfileOut, responses=CONSENT)
def save_profile(body: CVProfile, user: CurrentUser) -> ProfileOut:
    """Save the reviewed profile as confirmed. The uploaded CV file is deleted."""
    raise not_implemented("2.3")


@router.get("/profile", response_model=ProfileOut, responses=NOT_FOUND)
def get_profile(user: CurrentUser) -> ProfileOut:
    """The confirmed profile; 404 if none has been confirmed."""
    raise not_implemented("2.3")
