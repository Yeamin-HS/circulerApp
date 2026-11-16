"""API contract v1 (Story 1.5, ADR-010). Frozen: docs/openapi.json is the snapshot.

Read docs/API.md before changing anything here; the contract test fails on any difference.
"""

from datetime import date, datetime
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")

DegreeLevel = Literal["Class 8", "JSC", "SSC", "HSC", "Diploma", "Bachelor", "Masters", "PhD"]
Role = Literal["seeker", "admin"]
SourceType = Literal["digital", "scanned", "bijoy"]
ApplyMode = Literal["online", "post_or_in_person", "email_or_in_person"]
Verdict = Literal["eligible", "not_eligible", "unclear"]
CheckName = Literal["age", "degree", "result", "experience", "subject"]
CheckStatus = Literal["pass", "fail", "unknown"]
Route = Literal["fact_lookup", "eligibility", "summary", "out_of_scope"]
# "c:<chunk_id>" a passage, "p" the profile, "e:<post_id>" an eligibility result (AGENT.md §3)
SourceId = Annotated[str, Field(pattern=r"^(c:\d+|p|e:\d+)$")]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------- errors ----------

ErrorCode = Literal[
    "validation_error",  # 422 body or query failed validation
    "unauthorized",  # 401 missing, invalid or expired token
    "forbidden",  # 403 wrong role
    "not_found",  # 404 also returned for another user's resource
    "email_taken",  # 409 register
    "invalid_credentials",  # 401 login
    "consent_required",  # 403 CV or profile call before consent
    "profile_required",  # 409 eligibility or ask needs a confirmed profile
    "file_too_large",  # 413
    "unsupported_file",  # 415 type or magic bytes
    "too_many_pages",  # 422 circular over 20 pages
    "unreadable_file",  # 422 no text could be extracted
    "rate_limited",  # 429 per-IP limit or the LLM free tier is busy
    "not_implemented",  # 501 route not built yet
    "internal_error",  # 500
]


class ErrorBody(Model):
    code: ErrorCode
    message: str
    retry_after: int | None = Field(None, description="Seconds; set with rate_limited")


class ErrorResponse(Model):
    error: ErrorBody


# ---------- auth and account ----------


class RegisterRequest(Model):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(Model):
    email: EmailStr
    password: str = Field(max_length=128)


class TokenResponse(Model):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(description="Seconds until the token expires (3600)")


class UserOut(Model):
    id: int
    email: EmailStr
    role: Role
    consent_at: datetime | None
    has_confirmed_profile: bool
    created_at: datetime


class ConsentRequest(Model):
    accepted: Literal[True]


# ---------- profile ----------


class Degree(Model):
    level: DegreeLevel
    subject: str | None = None
    institution: str | None = None
    result: float | None = Field(None, description="CGPA or GPA")
    result_scale: float | None = Field(None, description="4.0 or 5.0")
    division: str | None = Field(None, description="Older results, e.g. '1st division'")
    passing_year: int | None = None


class Experience(Model):
    title: str
    organisation: str | None = None
    start: date | None = None
    end: date | None = Field(None, description="null = current job")


class CVProfile(Model):
    full_name: str
    date_of_birth: date | None = None
    degrees: list[Degree] = []
    experience: list[Experience] = []
    skills: list[str] = []
    certifications: list[str] = []


class CVDraft(Model):
    """Extracted from the uploaded CV. Not stored until PUT /me/profile."""

    profile: CVProfile
    warnings: list[str] = Field([], description="e.g. hidden text found in the file")


class ProfileOut(Model):
    profile: CVProfile
    confirmed_at: datetime
    version: int = Field(description="Increases on every save; part of the answer cache key")


# ---------- circulars ----------


class Evidence(Model):
    chunk_id: int
    quote: str = Field(description="Exact substring of the chunk text")


class FieldValue(Model, Generic[T]):
    value: T | None = Field(None, description="null = not stated in the circular")
    evidence: list[Evidence] = []


# Concrete subclasses so the OpenAPI schema names are readable (StrField, not FieldValue_str_).
class StrField(FieldValue[str]): ...


class IntField(FieldValue[int]): ...


class FloatField(FieldValue[float]): ...


class DateField(FieldValue[date]): ...


class StrListField(FieldValue[list[str]]): ...


class DegreeField(FieldValue[DegreeLevel]): ...


class ApplyModeField(FieldValue[ApplyMode]): ...


class PostReq(Model):
    title: StrField
    vacancies: IntField
    grade: StrField
    min_degree: DegreeField
    subjects: StrListField
    min_result: StrField
    experience_years: FloatField
    age_limit: IntField = Field(description="Set only when it differs from the circular's")


class FactCard(Model):
    organisation: StrField
    posts: list[PostReq]
    deadline: DateField
    age_limit: IntField
    age_as_of: DateField
    fee: StrField
    apply_mode: ApplyModeField
    how_to_apply: StrField
    apply_link: StrField


class PostOut(Model):
    id: int
    requirements: PostReq


class VerdictCounts(Model):
    eligible: int
    not_eligible: int
    unclear: int


class CircularSummary(Model):
    id: int
    title: str
    organisation: str | None
    source_type: SourceType
    deadline: date | None
    created_at: datetime
    verdicts: VerdictCounts | None = Field(description="null without a confirmed profile")


class CircularDetail(Model):
    id: int
    title: str
    source_type: SourceType
    pages: int
    created_at: datetime
    fact_card: FactCard
    posts: list[PostOut] = Field(description="Same order as fact_card.posts, with ids")


class ChunkOut(Model):
    id: int
    circular_id: int
    post_id: int | None
    page: int
    kind: Literal["text", "table_row"]
    text: str


# ---------- eligibility ----------


class Check(Model):
    name: CheckName
    status: CheckStatus
    required: str | None = Field(description="What the circular asks, as short text")
    actual: str | None = Field(description="What the profile has, as short text")
    evidence: list[Evidence] = []


class PostEligibility(Model):
    post_id: int
    title: str
    verdict: Verdict
    checks: list[Check]
    gaps: list[str] = Field(description="One line per failed or unknown check (FR-13)")


class EligibilityReport(Model):
    circular_id: int
    profile_version: int
    posts: list[PostEligibility]


# ---------- ask (server-sent events) ----------


class AskRequest(Model):
    question: str = Field(min_length=1, max_length=500)


class TokenEvent(Model):
    """`event: token`. One piece of the draft while it streams."""

    text: str


class CitationEvent(Model):
    """`event: citation`. Sources the current answer cites."""

    ids: list[SourceId]


class SentenceVerdict(Model):
    text: str
    verdict: Literal["supported", "unsupported", "not_a_claim"]
    reason: str


class CritiqueEvent(Model):
    """`event: critique`. Result of one critique round."""

    round: int
    passed: bool
    sentences: list[SentenceVerdict]


class StatusEvent(Model):
    """`event: status`. Progress, or the LLM free tier being busy."""

    state: Literal["routing", "searching", "verifying", "revising", "busy"]
    retry_after: int | None = Field(None, description="Seconds; set when state is busy")


class FinalEvent(Model):
    """`event: final`. Always the last event. Replaces any streamed draft text."""

    answer: str
    outcome: Literal["answered", "abstained", "refused"]
    language: Literal["bn", "en"]
    route: Route
    citations: list[SourceId]
    n_llm_calls: int
    cached: bool


class AskEvents(Model):
    """Not a response body: lists the payload of each SSE event for the OpenAPI schema."""

    token: TokenEvent
    citation: CitationEvent
    critique: CritiqueEvent
    status: StatusEvent
    final: FinalEvent


class Health(Model):
    status: Literal["ok"]
