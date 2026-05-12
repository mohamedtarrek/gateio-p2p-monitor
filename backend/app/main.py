"""
Gate.io P2P Monitor - FastAPI Application
Main entry point for the backend server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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

# CORS configuration - allow all origins for Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes FIRST (before static files)
app.include_router(api_router)

# Try multiple possible paths for frontend build
possible_paths = [
    os.path.join(os.path.dirname(__file__), "../../frontend/out"),  # Local dev
    os.path.join(os.path.dirname(__file__), "../frontend/out"),       # Alternative
    os.path.join(os.path.dirname(__file__), "frontend/out"),        # Another alternative
    "/app/frontend/out",                                             # Docker/Railway absolute
    "./frontend/out",                                                # Relative
    os.path.join(os.getcwd(), "frontend/out"),                      # Current working dir
]

frontend_path = None
for path in possible_paths:
    if os.path.exists(path) and os.path.isdir(path):
        # Check if it has index.html
        if os.path.exists(os.path.join(path, "index.html")):
            frontend_path = path
            logger.info(f"Found frontend build at: {frontend_path}")
            break

if frontend_path:
    # Mount static files from _next directory (Next.js build output)
    next_static_path = os.path.join(frontend_path, "_next")
    if os.path.exists(next_static_path):
        app.mount("/_next", StaticFiles(directory=next_static_path), name="next-static")

    # Mount other static assets if they exist
    for static_dir in ["images", "assets", "static"]:
        static_path = os.path.join(frontend_path, static_dir)
        if os.path.exists(static_path):
            app.mount(f"/{static_dir}", StaticFiles(directory=static_path), name=static_dir)

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{path:path}", include_in_schema=False)
    async def serve_catch_all(path: str):
        # Skip API routes
        if path.startswith("api/") or path.startswith("docs") or path.startswith("openapi.json"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Try to serve the specific file
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fallback to index.html for client-side routing
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return JSONResponse({"detail": "Not Found"}, status_code=404)
else:
    logger.warning("Frontend build not found. Serving API only.")

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "Gate.io P2P Monitor API",
            "status": "running",
            "docs": "/docs",
            "api": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )
