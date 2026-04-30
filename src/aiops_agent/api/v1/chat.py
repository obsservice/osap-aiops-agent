import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

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
        }
    )


@router.post("")
async def chat():
    result = ""
    async for part in run_agent():
        result += part
    
    return JSONResponse(result)
