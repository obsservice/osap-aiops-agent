from collections.abc import Awaitable, Callable
from time import perf_counter

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = perf_counter()
        log = structlog.get_logger(__name__)

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - start_time) * 1000
            log.error(
                "request failed",
                method=request.method,
                path=request.url.path,
                query=str(request.url.query),
                client_host=request.client.host if request.client else None,
                request_id=getattr(request.state, "request_id", None),
                status_code=500,
                duration_ms=round(duration_ms, 2),
            )
            raise

        duration_ms = (perf_counter() - start_time) * 1000
        log.info(
            "request completed",
            method=request.method,
            path=request.url.path,
            query=str(request.url.query),
            client_host=request.client.host if request.client else None,
            request_id=getattr(request.state, "request_id", None),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        return response
