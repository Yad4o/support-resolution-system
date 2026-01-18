from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# TODO: import routers
# from app.api import auth, tickets, feedback, admin

# TODO: import settings
# from app.core.config import settings


def create_app() -> FastAPI:
    """
    Application factory.
    Creates and configures the FastAPI app.
    """
    app = FastAPI(
        title="Automated Customer Support Resolution System",
        description="Backend service for auto-resolving customer support tickets using AI",
        version="0.1.0",
    )

    # -----------------------------
    # TODO: Middleware configuration
    # -----------------------------

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------
    # TODO: Include API routers
    # -----------------------------

    # app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    # app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
    # app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
    # app.include_router(admin.router, prefix="/admin", tags=["Admin"])

    # -----------------------------
    # TODO: Startup & shutdown events
    # -----------------------------

    @app.on_event("startup")
    async def startup_event():
        """
        Runs when the application starts.
        """
        # TODO: Initialize database connection
        # TODO: Warm up AI models (optional)
        # TODO: Connect to Redis (if used)
        pass

    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Runs when the application shuts down.
        """
        # TODO: Close database connection
        # TODO: Gracefully shutdown background workers
        pass

    return app


# Create app instance
app = create_app()


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "ok",
        "service": "customer-support-resolution",
    }
