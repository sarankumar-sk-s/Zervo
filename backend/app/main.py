from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine, Base
from app.api.v1.api import api_router
from app.models import *  # Ensure all models are registered

# Automatically create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="ZERVO Community Food Redistribution API (FastAPI + Supabase PostgreSQL)"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Also support direct /api/ai/extract-food route as requested
from app.api.v1.ai import router as ai_router
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {"status": "ok", "database": settings.active_database_url.split("@")[-1]}
