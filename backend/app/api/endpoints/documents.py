"""Document management endpoints."""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import List, Optional
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime
import glob

from app.models import (
    DocumentUploadResponse, DocumentInfo, 
    SearchRequest, SearchResponse, SuccessResponse
)
from app.dependencies import get_rag_service
from app.services.rag_service import RAGService

router = APIRouter()

def generate_filename_with_timestamp(original_filename: str, upload_dir: Path) -> tuple[str, str]:
    """Generate filename with timestamp and running number."""
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get file extension
    file_path = Path(original_filename)
    file_extension = file_path.suffix.lower()
    file_stem = file_path.stem
    
    # Find existing files with same timestamp pattern
    pattern = f"{file_stem}_{timestamp}_*.{file_extension.lstrip('.')}" if file_extension else f"{file_stem}_{timestamp}_*"
    existing_files = glob.glob(str(upload_dir / pattern))
    
    # Calculate running number
    running_number = len(existing_files) + 1
    
    # Generate new filename and document ID
    new_filename = f"{file_stem}_{timestamp}_{running_number:03d}{file_extension}"
    document_id = f"{file_stem}_{timestamp}_{running_number:03d}"
    
    return new_filename, document_id

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    process_immediately: bool = Form(True),
    rag_service: RAGService = Depends(get_rag_service)
) -> DocumentUploadResponse:
    """
    Upload a document to the system.
    
    - **file**: Document file to upload
    - **metadata**: Optional metadata as JSON string
    - **process_immediately**: Whether to process the document immediately
    """
    try:
        # Create upload directory if not exists
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp and running number
        saved_filename, document_id = generate_filename_with_timestamp(file.filename, upload_dir)
        file_path = upload_dir / saved_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse metadata
        import json
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                parsed_metadata = {"raw_metadata": metadata}
        
        parsed_metadata.update({
            "original_filename": file.filename,
            "saved_filename": saved_filename,
            "file_size": file_path.stat().st_size,
            "document_id": document_id,
            "upload_timestamp": datetime.now().isoformat()
        })
        
        if process_immediately:
            # Ensure RAG service is initialized
            if not rag_service.initialized:
                await rag_service.initialize()
            
            # Process the document
            result = await rag_service.add_documents([str(file_path.parent)])
            
            if result.get("success", False):
                status = "processed"
                message = "Document uploaded and processed successfully"
            else:
                status = "processing_failed"
                message = f"Document uploaded but processing failed: {result.get('message', 'Unknown error')}"
        else:
            status = "uploaded"
            message = "Document uploaded successfully, processing pending"
        print(f"Document upload status: {status}, message: {message}")
        return DocumentUploadResponse(
            document_id=document_id,
            status=status,
            message=message,
            metadata=parsed_metadata
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.post("/bulk-process", response_model=SuccessResponse)
async def process_folder(
    folder_paths: List[str],
    rag_service: RAGService = Depends(get_rag_service)
) -> SuccessResponse:
    """
    Process documents from specified folder paths.
    
    - **folder_paths**: List of folder paths to process
    """
    try:
        # Validate folder paths
        valid_paths = []
        for folder_path in folder_paths:
            path = Path(folder_path)
            if path.exists() and path.is_dir():
                valid_paths.append(str(path.absolute()))
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Folder path does not exist or is not a directory: {folder_path}"
                )
        
        result = await rag_service.add_documents(valid_paths)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Failed to process documents")
            )
        
        return SuccessResponse(
            message=result["message"],
            data=result.get("statistics", {})
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process folders: {str(e)}"
        )

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> SearchResponse:
    """
    Search for relevant documents.
    
    - **query**: Search query
    - **limit**: Maximum number of results
    - **similarity_threshold**: Minimum similarity score
    - **filters**: Additional filters (not implemented yet)
    """
    try:
        response = await rag_service.search_documents(
            query=request.query,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search documents: {str(e)}"
        )

@router.get("/list", response_model=List[DocumentInfo])
async def list_documents(
    rag_service: RAGService = Depends(get_rag_service)
) -> List[DocumentInfo]:
    """
    List all documents in the system (placeholder).
    """
    # TODO: Implement document listing from vector store
    return []

@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service)
) -> SuccessResponse:
    """
    Delete a document from the system (placeholder).
    """
    # TODO: Implement document deletion
    return SuccessResponse(
        message=f"Document {document_id} deletion not implemented yet"
    )

@router.get("/{document_id}/info", response_model=DocumentInfo)
async def get_document_info(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service)
) -> DocumentInfo:
    """
    Get information about a specific document (placeholder).
    """
    # TODO: Implement document info retrieval
    raise HTTPException(
        status_code=404,
        detail="Document info retrieval not implemented yet"
    )