"""Circular, eligibility, ask and chunk routes (contract only; built in Epics 3 and 4)."""

from fastapi import APIRouter, UploadFile
from fastapi.sse import EventSourceResponse

from app.api.deps import AUTH_ERRORS, NOT_FOUND, UPLOAD_ERRORS, CurrentUser
from app.core.errors import not_implemented
from app.core.schemas import (
    AskEvents,
    AskRequest,
    ChunkOut,
    CircularDetail,
    CircularSummary,
    EligibilityReport,
    ErrorResponse,
)

router = APIRouter(tags=["circulars"], responses=AUTH_ERRORS)
NEEDS_PROFILE = {409: {"model": ErrorResponse}}
ASK_STREAM = {
    200: {
        "model": AskEvents,
        "description": "Server-sent events: token, citation, critique, status, final. "
        "The data of each event is the JSON of the property with the same name.",
    },
    429: {"model": ErrorResponse},
}


@router.post("/circulars", status_code=201, response_model=CircularDetail, responses=UPLOAD_ERRORS)
def upload_circular(file: UploadFile, user: CurrentUser) -> CircularDetail:
    """Upload a circular (PDF, JPG or PNG; at most 10 MB and 20 pages) and ingest it."""
    raise not_implemented("3.1")


@router.get("/circulars", response_model=list[CircularSummary])
def list_circulars(user: CurrentUser) -> list[CircularSummary]:
    """The user's circulars, earliest deadline first; no deadline last."""
    raise not_implemented("3.1")


@router.get("/circulars/{circular_id}", response_model=CircularDetail, responses=NOT_FOUND)
def get_circular(circular_id: int, user: CurrentUser) -> CircularDetail:
    """Fact card and posts of one circular."""
    raise not_implemented("3.2")


@router.get(
    "/circulars/{circular_id}/eligibility",
    response_model=EligibilityReport,
    responses=NOT_FOUND | NEEDS_PROFILE,
)
def get_eligibility(circular_id: int, user: CurrentUser) -> EligibilityReport:
    """Per-post verdicts against the confirmed profile, with evidence."""
    raise not_implemented("3.3")


@router.post(
    "/circulars/{circular_id}/ask",
    response_class=EventSourceResponse,
    responses=ASK_STREAM | NOT_FOUND,
)
def ask(circular_id: int, body: AskRequest, user: CurrentUser) -> EventSourceResponse:
    """Ask a question about one circular. The answer streams as server-sent events."""
    raise not_implemented("4.2")


@router.get("/chunks/{chunk_id}", response_model=ChunkOut, responses=NOT_FOUND)
def get_chunk(chunk_id: int, user: CurrentUser) -> ChunkOut:
    """Source text of one chunk, for citation highlighting."""
    raise not_implemented("3.2")
