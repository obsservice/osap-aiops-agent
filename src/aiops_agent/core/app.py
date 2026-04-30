from dataclasses import dataclass

from aiops_agent.core.config import Settings

_app_context: "AppContext | None" = None


@dataclass
class AppContext:
    settings: Settings


def get_app_context() -> AppContext:
    if _app_context is None:
        raise RuntimeError("Application context has not been initialized.")
    return _app_context


def reset_app_context() -> None:
    global _app_context
    _app_context = None
