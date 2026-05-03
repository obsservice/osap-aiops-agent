from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from starlette.types import Lifespan
import structlog

from aiops_agent.core.app import AppContext, reset_app_context, set_app_context
from aiops_agent.core.config import get_settings
from aiops_agent.core.logging import setup_logging
from aiops_agent.services.agent_service import AgentService
from harness_agent.graphs.graph import make_lead_graph


def create_lifespan() -> Lifespan[FastAPI]:
    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
        settings = get_settings()
        setup_logging(settings)
        log = structlog.get_logger(__name__)
        log.info("service starting")

        lead_agent = make_lead_graph()
        agent_service = AgentService(lead_agent)
        context = AppContext(settings, agent_service)
        set_app_context(context)

        try:
            yield {"context": context}
        finally:
            log.info("service stopping")
            reset_app_context()

    return _lifespan
