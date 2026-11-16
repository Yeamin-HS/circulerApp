from fastapi import FastAPI

from app.api import auth, circulars, me
from app.core import errors
from app.core.schemas import Health

app = FastAPI(title="Ask the Circular", version="0.1.0")
errors.install(app)
for module in (auth, me, circulars):
    app.include_router(module.router)


@app.get("/health", response_model=Health, tags=["health"])
def health() -> Health:
    """Warm-up ping (ARCHITECTURE §7)."""
    return Health(status="ok")
