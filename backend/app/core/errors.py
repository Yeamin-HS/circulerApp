"""One error shape for the whole API: {"error": {"code", "message", "retry_after"}}."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.schemas import ErrorBody, ErrorCode, ErrorResponse

STATUS_CODES: dict[int, ErrorCode] = {
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    413: "file_too_large",
    415: "unsupported_file",
    429: "rate_limited",
}


class ApiError(Exception):
    def __init__(
        self, status: int, code: ErrorCode, message: str, retry_after: int | None = None
    ) -> None:
        self.status, self.code, self.message, self.retry_after = status, code, message, retry_after


def _response(status: int, code: ErrorCode, message: str, retry_after: int | None = None):
    body = ErrorResponse(error=ErrorBody(code=code, message=message, retry_after=retry_after))
    headers = {"Retry-After": str(retry_after)} if retry_after else None
    return JSONResponse(body.model_dump(), status_code=status, headers=headers)


def not_implemented(story: str) -> ApiError:
    return ApiError(501, "not_implemented", f"Not built yet; arrives in Story {story}.")


def install(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error(_: Request, exc: ApiError) -> JSONResponse:
        return _response(exc.status, exc.code, exc.message, exc.retry_after)

    @app.exception_handler(RequestValidationError)
    async def invalid(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"])
        return _response(422, "validation_error", f"{where}: {first['msg']}")

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        code = STATUS_CODES.get(exc.status_code, "internal_error")
        return _response(exc.status_code, code, str(exc.detail))
