from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aiops_agent.api.exception_handlers import register_exception_handlers
from aiops_agent.api.router import api_router
from aiops_agent.core.lifespan import create_lifespan
from aiops_agent.middlewares.logging import RequestLoggingMiddleware
from aiops_agent.middlewares.request_id import RequestIDMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="osap-aiops-agent",
        version="0.1.0",
        description="An AIOps agent for the OSAP platform.",
        lifespan=create_lifespan(),
    )

    # middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # exception
    register_exception_handlers(app)

    # router
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint.

        Returns:
            Service health status information.
        """
        return {"status": "healthy", "service": "osap-aiops-agent"}

    return app


# Create app instance for uvicorn
app = create_app()
