"""Settings from environment variables, with the repo-root .env as a fallback for local work."""

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

ENV_FILE = Path(__file__).parents[3] / ".env"


def _load_env_file() -> None:
    """Minimal .env reader: KEY=value lines; real environment variables win."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.strip().partition("=")
        if sep and key and not key.startswith("#"):
            os.environ.setdefault(key, value.strip().strip("\"'"))


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return "sqlite:///./dev.db"  # ADR-011: local fallback
    if url.startswith(("postgres://", "postgresql://")):
        return "postgresql+psycopg://" + url.split("://", 1)[1]
    return url


def _jwt_secret(production: bool) -> str:
    secret = os.environ.get("JWT_SECRET", "").strip()
    if secret:
        return secret
    if production:
        raise RuntimeError("JWT_SECRET must be set when APP_ENV=production")
    return secrets.token_urlsafe(48)  # dev only: tokens stop working when the server restarts


@dataclass(frozen=True)
class Settings:
    production: bool
    database_url: str
    jwt_secret: str
    jwt_minutes: int = 60
    cors_origins: list[str] = field(default_factory=list)


def load() -> Settings:
    _load_env_file()
    production = os.environ.get("APP_ENV", "development") == "production"
    origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
    return Settings(
        production=production,
        database_url=_database_url(),
        jwt_secret=_jwt_secret(production),
        cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
    )


settings = load()
