from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, circulars, me
from app.core import errors
from app.core.config import settings
from app.core.schemas import Health
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Ask the Circular", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
errors.install(app)
for module in (auth, me, circulars):
    app.include_router(module.router)


@app.get("/health", response_model=Health, tags=["health"])
def health() -> Health:
    """Warm-up ping (ARCHITECTURE §7)."""
    return Health(status="ok")
