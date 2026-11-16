"""Small in-memory per-IP rate limit (NFR-09). One process only; enough for one free dyno."""

import time
from collections import defaultdict, deque

from fastapi import Request

from app.core.errors import ApiError


class RateLimit:
    """FastAPI dependency: at most `limit` calls per `window` seconds from one IP."""

    def __init__(self, limit: int, window: int) -> None:
        self.limit, self.window = limit, window
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        forwarded = request.headers.get("x-forwarded-for", "")  # set by Render's proxy
        ip = forwarded.split(",")[0].strip() or (request.client.host if request.client else "?")
        now = time.monotonic()
        hits = self.hits[ip]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            wait = int(self.window - (now - hits[0])) + 1
            raise ApiError(429, "rate_limited", "Too many attempts. Try again later.", wait)
        hits.append(now)
        if len(self.hits) > 10_000:  # do not grow without bound
            self.hits.clear()
