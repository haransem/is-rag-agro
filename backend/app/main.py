"""Main FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import sys
import os
from pathlib import Path

# Add legacy mypkg to path for backward compatibility  
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.config import router as config_router  
from app.api.endpoints.documents import router as documents_router
from app.api.endpoints.status import router as status_router
from app.core.config import get_settings
from app.services.rag_service import RAGService
from app.dependencies import set_rag_service

# Global RAG service instance
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    global rag_service
    
    # Startup
    print("🚀 Starting Agriculture RAG API...")
    settings = get_settings()
    rag_service = RAGService(settings)
    
    # Initialize with default configuration
    await rag_service.initialize()
    print("✅ RAG Service initialized")
    
    # Set global service for dependency injection
    set_rag_service(rag_service)
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Agriculture RAG API...")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Agriculture RAG API",
        description="Backend API for Agriculture RAG System with configurable pipeline",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(config_router, prefix="/api/v1/config", tags=["config"])
    app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(status_router, prefix="/api/v1/status", tags=["status"])
    
    # Serve static files (frontend)
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "agriculture-rag-api"}
    
    return app

# Create app instance
app = create_app()

def get_rag_service() -> RAGService:
    """Get global RAG service instance."""
    from app.dependencies import get_rag_service as _get_rag_service
    return _get_rag_service()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )