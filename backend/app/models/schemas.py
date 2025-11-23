"""Pydantic models for API requests and responses."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat request model."""
    question: str = Field(..., description="User question")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    include_sources: bool = Field(True, description="Include source documents")
    debug: bool = Field(False, description="Enable debug information")


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents")
    conversation_id: str = Field(..., description="Conversation ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information")


class DocumentUploadRequest(BaseModel):
    """Document upload request model."""
    file_path: str = Field(..., description="Path to uploaded file")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")
    process_immediately: bool = Field(True, description="Process document immediately")


class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    document_id: str = Field(..., description="Unique document ID")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class DocumentInfo(BaseModel):
    """Document information model."""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type/extension")
    file_size: int = Field(..., description="File size in bytes")
    upload_time: datetime = Field(..., description="Upload timestamp")
    status: str = Field(..., description="Processing status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    chunk_count: Optional[int] = Field(None, description="Number of chunks generated")


class ConfigUpdateRequest(BaseModel):
    """Configuration update request model."""
    category: str = Field(..., description="Configuration category (database, models, processing)")
    settings: Dict[str, Any] = Field(..., description="Settings to update")


class ConfigResponse(BaseModel):
    """Configuration response model."""
    category: str = Field(..., description="Configuration category")
    current_settings: Dict[str, Any] = Field(..., description="Current configuration")
    available_options: Optional[Dict[str, Any]] = Field(None, description="Available options")


class SystemStatus(BaseModel):
    """System status model."""
    status: str = Field(..., description="Overall system status")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Component statuses")
    statistics: Dict[str, Any] = Field(..., description="System statistics")
    last_updated: datetime = Field(..., description="Last update timestamp")


class SearchRequest(BaseModel):
    """Document search request model."""
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")
    similarity_threshold: float = Field(default=0.0, description="Minimum similarity score")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class SearchResult(BaseModel):
    """Search result model."""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    score: float = Field(..., description="Similarity score")


class SearchResponse(BaseModel):
    """Search response model."""
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original query")
    execution_time: float = Field(..., description="Search execution time in seconds")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class SuccessResponse(BaseModel):
    """Generic success response model."""
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")