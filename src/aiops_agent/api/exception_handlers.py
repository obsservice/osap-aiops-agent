from http import HTTPStatus
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from aiops_agent.core.exceptions import AppErr
from aiops_agent.schemas.response import create_error_response


log = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppErr, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(ResponseValidationError, response_validation_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def app_error_handler(
    request: Request,
    exc: AppErr,
) -> JSONResponse:
    log.warning(
        "app error",
        **_request_log_fields(request),
        status_code=exc.status_code,
        code=exc.code,
        detail=exc.detail,
    )

    return create_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
        headers=exc.headers,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    log.warning(
        "http exception",
        **_request_log_fields(request),
        status_code=exc.status_code,
        detail=exc.detail,
    )

    detail = exc.detail
    return create_error_response(
        status_code=exc.status_code,
        code=_http_error_code(exc.status_code),
        message=detail if isinstance(detail, str) else _status_phrase(exc.status_code),
        detail=None if isinstance(detail, str) else detail,
        headers=exc.headers,
    )


async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = exc.errors()
    log.warning(
        "request validation failed",
        **_request_log_fields(request),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors,
    )

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="REQUEST_VALIDATION_ERROR",
        message="Request validation failed.",
        detail=errors,
    )


async def response_validation_handler(
    request: Request,
    exc: ResponseValidationError,
) -> JSONResponse:
    log.error(
        "response validation failed",
        **_request_log_fields(request),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=exc.errors(),
    )

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="RESPONSE_VALIDATION_ERROR",
        message="Internal server error.",
    )


async def pydantic_validation_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    errors = exc.errors()
    log.warning(
        "pydantic validation failed",
        **_request_log_fields(request),
        status_code=status.HTTP_400_BAD_REQUEST,
        errors=errors,
    )

    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        message="Validation failed.",
        detail=errors,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    log.exception(
        "unhandled exception",
        **_request_log_fields(request),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error=str(exc),
    )

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="Internal server error.",
    )


def _request_log_fields(request: Request) -> dict[str, Any]:
    return {
        "method": request.method,
        "path": request.url.path,
        "query": str(request.url.query),
        "client_host": request.client.host if request.client else None,
        "request_id": _request_id(request),
    }


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _status_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "HTTP error"


def _http_error_code(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).name
    except ValueError:
        return "HTTP_ERROR"
