"""Configuration management endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.models import ConfigUpdateRequest, ConfigResponse, SuccessResponse
from app.dependencies import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter()

@router.get("/{category}", response_model=ConfigResponse)
async def get_config(
    category: str,
    rag_service: RAGService = Depends(get_rag_service)
) -> ConfigResponse:
    """
    Get current configuration for a category.
    
    - **category**: Configuration category (database, models, processing)
    """
    if category not in ["database", "models", "processing"]:
        raise HTTPException(
            status_code=400,
            detail="Category must be one of: database, models, processing"
        )
    
    try:
        current_settings = rag_service.get_current_config(category)
        
        # Define available options for each category
        available_options = {}
        
        if category == "models":
            available_options = {
                "embedding_models": ["nomic-embed-text", "mxbai-embed-large"],
                "llm_models": ["gemma3:27b", "gemma3:8b", "llama3:8b", "mistral:7b"],
                "retriever_k_range": [1, 20],
                "temperature_range": [0.0, 2.0],
                "max_tokens_range": [100, 4096]
            }
        elif category == "processing":
            available_options = {
                "chunk_size_range": [200, 2000],
                "chunk_overlap_range": [50, 500],
                "supported_extensions": [".pdf", ".docx", ".pptx", ".xlsx", ".csv", ".txt", ".jpg", ".png"],
                "max_file_size_mb_range": [1, 100],
                "ocr_languages": ["tha", "eng", "chi_sim", "jpn"]
            }
        elif category == "database":
            available_options = {
                "collection_name_examples": ["agro_documents", "agriculture_kb", "agro_data"],
                "chroma_db_impl_options": ["duckdb+parquet", "sqlite"]
            }
        
        return ConfigResponse(
            category=category,
            current_settings=current_settings,
            available_options=available_options
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get configuration: {str(e)}"
        )

@router.put("/{category}", response_model=SuccessResponse)
async def update_config(
    category: str,
    request: ConfigUpdateRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> SuccessResponse:
    """
    Update configuration for a category.
    
    - **category**: Configuration category (database, models, processing)
    - **settings**: Dictionary of settings to update
    """
    if category not in ["database", "models", "processing"]:
        raise HTTPException(
            status_code=400,
            detail="Category must be one of: database, models, processing"
        )
    
    try:
        result = await rag_service.update_configuration(category, request.settings)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Configuration update failed")
            )
        
        return SuccessResponse(
            message=result["message"],
            data=result.get("updated_settings", {})
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )

@router.get("/", response_model=Dict[str, Any])
async def get_all_configs(
    rag_service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """
    Get all current configurations.
    """
    try:
        all_configs = {}
        for category in ["database", "models", "processing"]:
            all_configs[category] = rag_service.get_current_config(category)
        
        return {
            "configurations": all_configs,
            "categories": ["database", "models", "processing"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get configurations: {str(e)}"
        )

@router.post("/reset/{category}", response_model=SuccessResponse)
async def reset_config(
    category: str,
    rag_service: RAGService = Depends(get_rag_service)
) -> SuccessResponse:
    """
    Reset configuration for a category to defaults.
    """
    if category not in ["database", "models", "processing"]:
        raise HTTPException(
            status_code=400,
            detail="Category must be one of: database, models, processing"
        )
    
    try:
        # Define default settings
        defaults = {}
        
        if category == "database":
            defaults = {
                "persist_directory": "./data/chroma_db",
                "collection_name": "agro_documents"
            }
        elif category == "models":
            defaults = {
                "embedding_model": "nomic-embed-text",
                "llm_model": "gemma3:27b",
                "retriever_k": 5,
                "temperature": 0.1,
                "max_tokens": 2048
            }
        elif category == "processing":
            defaults = {
                "chunk_size": 800,
                "chunk_overlap": 150,
                "max_file_size_mb": 50,
                "enable_ocr": True
            }
        
        result = await rag_service.update_configuration(category, defaults)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Configuration reset failed")
            )
        
        return SuccessResponse(
            message=f"Configuration for {category} reset to defaults",
            data=defaults
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset configuration: {str(e)}"
        )