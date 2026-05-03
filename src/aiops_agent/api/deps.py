from typing import Annotated
from fastapi import Depends, Request

from aiops_agent.core.app import AppContext, get_app_context

ContextDep = Annotated[AppContext, Depends(get_app_context)]


def get_request_id(req: Request) -> str:
    req_id = getattr(req.state, "request_id")
    return req_id if isinstance(req_id, str) else ""

RequestIdDep = Annotated[str, Depends(get_request_id)]
