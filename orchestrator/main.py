"""
SystemCrafter AI - Main Application Entry Point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from orchestrator.api import auth_router, projects_router, tasks_router, ws_router
from orchestrator.core import get_settings, init_db, setup_logging
from orchestrator.schemas import HealthCheck

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Auto-Architecture Generator - Converts product descriptions into production-ready applications",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check() -> HealthCheck:
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        version=settings.app_version,
        database="connected",
        redis="connected",
    )
