from fastapi import FastAPI

app = FastAPI(title="Ask the Circular", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Warm-up ping (ARCHITECTURE §7)."""
    return {"status": "ok"}
