"""System status endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.models import SystemStatus, SuccessResponse
from app.dependencies import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter()

@router.get("/", response_model=SystemStatus)
async def get_system_status(
    rag_service: RAGService = Depends(get_rag_service)
) -> SystemStatus:
    """
    Get comprehensive system status.
    
    Returns information about:
    - Database status and document count
    - Model status and availability
    - Processing configuration
    - System statistics
    """
    try:
        status = await rag_service.get_system_status()
        return status
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    """
    return {"status": "healthy", "service": "agriculture-rag-api"}

@router.post("/reset", response_model=SuccessResponse)
async def reset_system(
    confirm: bool = False,
    rag_service: RAGService = Depends(get_rag_service)
) -> SuccessResponse:
    """
    Reset the entire system (placeholder for safety).
    
    - **confirm**: Must be True to proceed with reset
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Reset must be confirmed by setting confirm=True"
        )
    
    try:
        # TODO: Implement system reset
        # This should:
        # 1. Clear vector database
        # 2. Reset configurations to defaults
        # 3. Clear uploaded files
        # 4. Re-initialize system
        
        return SuccessResponse(
            message="System reset not implemented yet for safety reasons"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset system: {str(e)}"
        )

@router.get("/models")
async def get_available_models(
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """
    Get available AI models.
    """
    try:
        status = await rag_service.get_system_status()
        models_info = status.components.get("models", {})
        
        return {
            "current": {
                "embedding_model": models_info.get("embedding_model"),
                "llm_model": models_info.get("llm_model")
            },
            "available": {
                "embedding_models": ["nomic-embed-text", "mxbai-embed-large"],
                "llm_models": models_info.get("available_models", []),
                "recommended": {
                    "embedding": "nomic-embed-text",
                    "llm_small": "gemma3:8b", 
                    "llm_large": "gemma3:27b"
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available models: {str(e)}"
        )

@router.get("/statistics")
async def get_statistics(
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """
    Get detailed system statistics.
    """
    try:
        status = await rag_service.get_system_status()
        
        return {
            "documents": {
                "total": status.statistics.get("total_documents", 0),
                "by_type": {},  # TODO: Implement document type breakdown
                "processing_status": "active"
            },
            "performance": {
                "uptime": status.statistics.get("uptime", "unknown"),
                "last_query": status.statistics.get("last_query", "unknown"),
                "average_response_time": "unknown"  # TODO: Implement metrics
            },
            "storage": {
                "database_size": "unknown",  # TODO: Get actual database size
                "uploaded_files": "unknown"
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )