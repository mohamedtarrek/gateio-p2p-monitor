"""
Gate.io P2P Monitor - FastAPI Application
Main entry point for the backend server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.routers.api import router as api_router
from app.utils import setup_logger
from app.config import settings

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    logger.info("=" * 50)
    logger.info("Gate.io P2P Monitor Starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info("=" * 50)

    yield

    logger.info("Shutting down Gate.io P2P Monitor...")

# Create FastAPI app
app = FastAPI(
    title="Gate.io P2P Monitor",
    description="Real-time P2P price monitoring with Telegram notifications",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Serve frontend static files (for production deployment)
frontend_build_path = os.path.join(os.path.dirname(__file__), "../../frontend/out")
if os.path.exists(frontend_build_path):
    app.mount("/_next", StaticFiles(directory=os.path.join(frontend_build_path, "_next")), name="next-static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_build_path, "index.html"))

    @app.get("/{path:full_path}")
    async def serve_catch_all(path: str):
        # API routes are handled by the router, everything else goes to frontend
        if path.startswith("api/"):
            return {"detail": "Not Found"}
        file_path = os.path.join(frontend_build_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
