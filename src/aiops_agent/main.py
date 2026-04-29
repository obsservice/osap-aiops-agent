from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="osap-aiops-agent",
        version="0.1.0",
        description="An AIOps agent for the OSAP platform."
    )

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
