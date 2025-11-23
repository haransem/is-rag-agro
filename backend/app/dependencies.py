"""Dependency injection for FastAPI."""

from fastapi import HTTPException
from app.services.rag_service import RAGService

# Global RAG service instance
rag_service: RAGService = None

def get_rag_service() -> RAGService:
    """Get global RAG service instance."""
    global rag_service
    if rag_service is None:
        raise HTTPException(status_code=500, detail="RAG service not initialized")
    return rag_service

def set_rag_service(service: RAGService) -> None:
    """Set global RAG service instance."""
    global rag_service
    rag_service = service