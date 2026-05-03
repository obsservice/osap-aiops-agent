import asyncio
from collections.abc import AsyncIterator

from aiops_agent.schemas.context import RequestContext


class AgentService:

    def __init__(self, graph):
        self.graph = graph

    async def call(self, req: RequestContext):
        state = await self.graph.ainvoke(
            {
                "request_id": req.request_id,
                "user_query": _last_user_message(req),
            }
        )

        return {
            "results": state["results"]
        }

    async def stream(self, req: RequestContext) -> AsyncIterator[str]:
        result = await self.call(req)

        for token in result["results"]:
            yield token
            await asyncio.sleep(0)


def _last_user_message(req: RequestContext) -> str:
    for message in reversed(req.messages):
        if message.role == "user":
            return message.content or ""
    return ""
