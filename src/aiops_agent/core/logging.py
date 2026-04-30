import logging
import sys
import structlog
from typing import Any

from aiops_agent.core.config import Settings


def _add_module_name(
    logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    name = getattr(logger, "name", None)
    if name:
        event_dict["__name__"] = name
    return event_dict


def setup_logging(settings: Settings):
    # 标准 logging 基础配置
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # structlog 配置
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_module_name,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 统一 uvicorn 日志
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
