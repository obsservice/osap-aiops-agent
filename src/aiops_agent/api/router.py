from fastapi import APIRouter

from aiops_agent.api.v1 import chat


api_router = APIRouter(prefix="/v1")
api_router.include_router(chat.router)
