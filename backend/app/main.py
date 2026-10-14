"""
CivicPulse AI - FastAPI Main Application Server.
Provides civic issue reporting APIs, real-time analytics, 
spatial endpoints, administrative controls, and frontend static asset serving.
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.config import settings
from backend.app.database import init_db, get_db
from backend.app.routers import reports, analytics, map as map_router, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events: initialize DB and seeds on startup."""
    print("=" * 60)
    print("  CivicPulse AI - Smart Civic Reporting Platform Starting")
    print("=" * 60)
    # Initialize SQLite database and demo data
    init_db()
    print("[OK] SQLite database initialized & validated")
    print(f"[OK] Uploads directory mounted at: {settings.UPLOADS_DIR}")
    print(f"[OK] Swagger API docs live at: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)
    yield
    print("CivicPulse AI backend shutting down gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for seamless local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads directory for complaint and resolution images
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# Include Core API Routers
app.include_router(reports.router)
app.include_router(analytics.router)
app.include_router(map_router.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """System health check endpoint verifying database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "ai_vision_configured": bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10)
    }


# Mount Frontend if directory exists
if settings.FRONTEND_DIR.exists():
    # Mount css, js, assets
    css_dir = settings.FRONTEND_DIR / "css"
    js_dir = settings.FRONTEND_DIR / "js"
    assets_dir = settings.FRONTEND_DIR / "assets"

    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        """Serve the CivicPulse AI Dashboard frontend."""
        index_file = settings.FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse({"message": "Frontend index.html not yet built. Visit /docs for API."})
