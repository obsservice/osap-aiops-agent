from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from starlette.types import Lifespan
import structlog

from aiops_agent.core.app import AppContext, reset_app_context
from aiops_agent.core.config import get_settings
from aiops_agent.core.logging import setup_logging


def create_lifespan() -> Lifespan[FastAPI]:
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
        settings = get_settings()
        setup_logging(settings)
        log = structlog.get_logger(__name__)
        log.info("service starting")

        context = AppContext(settings)

        try:
            yield {"context": context}
        finally:
            log.info("service stopping")
            context.ready = False
            reset_app_context()

    return _lifespan
