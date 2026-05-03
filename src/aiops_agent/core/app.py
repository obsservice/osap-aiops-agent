from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiops_agent.core.config import Settings

if TYPE_CHECKING:
    from aiops_agent.services.agent_service import AgentService

_app_context: "AppContext | None" = None


@dataclass
class AppContext:
    settings: Settings
    agent: "AgentService"


def get_app_context() -> AppContext:
    if _app_context is None:
        raise RuntimeError("Application context has not been initialized.")
    return _app_context


def set_app_context(context: AppContext) -> None:
    global _app_context
    _app_context = context


def reset_app_context() -> None:
    global _app_context
    _app_context = None
