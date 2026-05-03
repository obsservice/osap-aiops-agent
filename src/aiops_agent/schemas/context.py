from dataclasses import dataclass
from typing import TYPE_CHECKING

from aiops_agent.schemas.chat import ChatMessage

if TYPE_CHECKING:
    from aiops_agent.core.app import AppContext


@dataclass
class RequestContext:
    request_id: str
    app_context: "AppContext"
    messages: list[ChatMessage]
