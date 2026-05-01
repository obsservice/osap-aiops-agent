from typing import Literal

from pydantic import BaseModel

ChatCompletionFinishReason = Literal[
    "stop",
    "length",
    "tool_calls",
    "content_filter",
    "function_call",
]


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None


class ChatCompletionRequest(BaseModel):
    model: str = "private-agent"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: ChatCompletionFinishReason | None = None


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage | None = None


class ChatCompletionChunkDelta(BaseModel):
    role: Literal["assistant", "tool"] | None = None
    content: str | None = None


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: ChatCompletionFinishReason | None = None


class ChatCompletionChunkResponse(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice]
    usage: ChatCompletionUsage | None = None
