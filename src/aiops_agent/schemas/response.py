from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: Any | None = None


def create_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    detail: Any | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    error = ErrorResponse(
        code=code,
        message=message,
        detail=detail,
    )

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(error.model_dump(exclude_none=True)),
        headers=headers,
    )
