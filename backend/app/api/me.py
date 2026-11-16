"""Account, consent and profile routes. CV and profile handling arrive in Story 2.3."""

from fastapi import APIRouter, UploadFile
from sqlalchemy import delete

from app.api.deps import (
    AUTH_ERRORS,
    NOT_FOUND,
    UPLOAD_ERRORS,
    ConsentedUser,
    CurrentUser,
    user_out,
)
from app.core.errors import not_implemented
from app.core.schemas import ConsentRequest, CVDraft, CVProfile, ErrorResponse, ProfileOut, UserOut
from app.db.models import User, utcnow
from app.db.session import Db

router = APIRouter(prefix="/me", tags=["me"], responses=AUTH_ERRORS)
CONSENT = {403: {"model": ErrorResponse}}


@router.get("", response_model=UserOut)
def get_me(user: CurrentUser) -> UserOut:
    """The signed-in user, with consent and profile state."""
    return user_out(user)


@router.delete("", status_code=204)
def delete_me(user: CurrentUser, db: Db) -> None:
    """Delete the account and all of its data. Cannot be undone."""
    # A database-level delete: rows in every table that points at this user go with it
    # through ON DELETE CASCADE (see owner_fk in app/db/models.py).
    db.execute(delete(User).where(User.id == user.id))
    db.commit()


@router.post("/consent", response_model=UserOut)
def give_consent(body: ConsentRequest, user: CurrentUser, db: Db) -> UserOut:
    """Record consent to store a profile. Required before /me/cv and /me/profile."""
    if user.consent_at is None:  # repeating the call keeps the first timestamp
        user.consent_at = utcnow()
        db.commit()
    return user_out(user)


@router.post("/cv", response_model=CVDraft, responses=UPLOAD_ERRORS | CONSENT)
def upload_cv(file: UploadFile, user: ConsentedUser) -> CVDraft:
    """Upload a CV (PDF or DOCX, at most 5 MB) and get a draft profile. Nothing is saved."""
    raise not_implemented("2.3")


@router.put("/profile", response_model=ProfileOut, responses=CONSENT)
def save_profile(body: CVProfile, user: ConsentedUser) -> ProfileOut:
    """Save the reviewed profile as confirmed. The uploaded CV file is deleted."""
    raise not_implemented("2.3")


@router.get("/profile", response_model=ProfileOut, responses=NOT_FOUND)
def get_profile(user: CurrentUser) -> ProfileOut:
    """The confirmed profile; 404 if none has been confirmed."""
    raise not_implemented("2.3")
