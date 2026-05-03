import asyncio
import json
import time
import uuid
from collections.abc import AsyncIterator

import structlog
from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from aiops_agent.api.deps import ContextDep, RequestIdDep
from aiops_agent.schemas.chat import (
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionChunkResponse,
    ChatCompletionChoice,
    ChatCompletionFinishReason,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)
from aiops_agent.schemas.context import RequestContext

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


async def run_agent():
    tokens = ["Hello", " ", "world", "!"]

    for t in tokens:
        yield f"data: {t}\n\n"
        await asyncio.sleep(0.3)


@router.post("/stream")
async def stream() -> StreamingResponse:
    return StreamingResponse(
        run_agent(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("")
async def chat():
    result = ""
    async for part in run_agent():
        result += part

    return JSONResponse(content=result)


def build_chat_completion_response(
    *,
    completion_id: str,
    created: int,
    model: str,
    content: str,
) -> ChatCompletionResponse:
    return ChatCompletionResponse(
        id=completion_id,
        created=created,
        model=model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=content),
                finish_reason="stop",
            ),
        ],
    )


def build_chat_completion_chunk(
    *,
    completion_id: str,
    created: int,
    model: str,
    content: str | None = None,
    finish_reason: ChatCompletionFinishReason | None = None,
) -> ChatCompletionChunkResponse:
    return ChatCompletionChunkResponse(
        id=completion_id,
        created=created,
        model=model,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(content=content),
                finish_reason=finish_reason,
            ),
        ],
    )


def format_sse_chunk(chunk: ChatCompletionChunkResponse) -> str:
    data = json.dumps(chunk.model_dump(exclude_none=True), ensure_ascii=False)
    return f"data: {data}\n\n"


@router.post(
    "/completions",
    response_model=ChatCompletionResponse,
    response_model_exclude_none=True,
)
async def chat_completions(req: ChatCompletionRequest, req_id: RequestIdDep, ctx: ContextDep) -> ChatCompletionResponse | StreamingResponse:
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    log.info(
        "chat completions requested",
        request_id=req_id,
        completion_id=completion_id,
        model=req.model,
        stream=req.stream,
        message_count=len(req.messages),
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )

    req_context = RequestContext(req_id, ctx, req.messages)
    if not req.stream:
        result = await ctx.agent.call(req_context)
        content = result["results"]
        return build_chat_completion_response(
            completion_id=completion_id,
            created=created,
            model=req.model,
            content=content,
        )

    async def sse_generator() -> AsyncIterator[str]:
        async for token in ctx.agent.stream(req_context):
            chunk = build_chat_completion_chunk(
                completion_id=completion_id,
                created=created,
                model=req.model,
                content=token,
            )
            yield format_sse_chunk(chunk)

        done_chunk = build_chat_completion_chunk(
            completion_id=completion_id,
            created=created,
            model=req.model,
            finish_reason="stop",
        )
        yield format_sse_chunk(done_chunk)
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
