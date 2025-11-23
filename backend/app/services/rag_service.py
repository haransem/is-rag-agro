"""RAG Service for managing the entire RAG pipeline."""

import asyncio
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import sys

# Import legacy components 
from mypkg import AgroRAGApplication
from mypkg.config import AppConfig, DatabaseConfig, ModelConfig, ProcessingConfig
from mypkg.document_processor import DocumentProcessor
from mypkg.vector_store import VectorStoreManager
from mypkg.rag_pipeline import RAGPipeline

from app.core.config import Settings
from app.models.schemas import (
    ChatResponse, DocumentInfo, SystemStatus, 
    SearchResult, SearchResponse
)


class RAGService:
    """Service class for managing RAG operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.rag_app: Optional[AgroRAGApplication] = None
        self.initialized = False
        self.document_registry: Dict[str, DocumentInfo] = {}
        self._processing_lock = asyncio.Lock()  # Add processing lock
        
    async def initialize(self) -> bool:
        """Initialize RAG service with current settings."""
        try:
            # Convert API settings to legacy config format
            legacy_config = self._convert_settings_to_legacy()
            
            # Initialize RAG application
            self.rag_app = AgroRAGApplication()
            self.rag_app.config = legacy_config
            
            # Re-initialize components with new config
            self.rag_app._initialize_components()
            
            # Setup database and vector store
            self.rag_app.setup_database(reset=False)
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize RAG service: {e}")
            return False
    
    def _convert_settings_to_legacy(self) -> AppConfig:
        """Convert API settings to legacy config format."""
        database_config = DatabaseConfig(
            persist_directory=self.settings.database.persist_directory,
            collection_name=self.settings.database.collection_name
        )
        
        model_config = ModelConfig(
            embedding_model=self.settings.models.embedding_model,
            llm_model=self.settings.models.llm_model,
            retriever_k=self.settings.models.retriever_k
        )
        
        processing_config = ProcessingConfig(
            chunk_size=self.settings.processing.chunk_size,
            chunk_overlap=self.settings.processing.chunk_overlap
        )
        
        return AppConfig(
            database=database_config,
            model=model_config,
            processing=processing_config
        )
    
    async def process_question(
        self, 
        question: str, 
        conversation_id: Optional[str] = None,
        include_sources: bool = True,
        debug: bool = False
    ) -> ChatResponse:
        """Process user question and generate response."""
        if not self.initialized:
            await self.initialize()
        
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Initialize RAG if not done yet
            if self.rag_app.rag_pipeline.retriever is None:
                self.rag_app.initialize_rag()
            
            # Get response from RAG
            answer = self.rag_app.query(question, debug=debug)
            
            sources = []
            debug_info = None
            
            if include_sources:
                # Get source documents
                docs = self.rag_app.rag_pipeline.retrieve_documents(question)
                sources = [
                    {
                        "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                        "metadata": doc.metadata,
                        "relevance_score": getattr(doc, 'score', 0.0)
                    }
                    for doc in docs
                ]
            
            if debug:
                debug_info = {
                    "model_config": {
                        "embedding_model": self.settings.models.embedding_model,
                        "llm_model": self.settings.models.llm_model,
                        "retriever_k": self.settings.models.retriever_k
                    },
                    "retrieved_docs_count": len(sources),
                    "processing_config": {
                        "chunk_size": self.settings.processing.chunk_size,
                        "chunk_overlap": self.settings.processing.chunk_overlap
                    }
                }
            
            return ChatResponse(
                answer=answer,
                sources=sources,
                conversation_id=conversation_id,
                metadata={
                    "question": question,
                    "timestamp": datetime.now().isoformat(),
                    "model_used": self.settings.models.llm_model
                },
                debug_info=debug_info
            )
            
        except Exception as e:
            return ChatResponse(
                answer=f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}",
                sources=[],
                conversation_id=conversation_id,
                metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
            )
    
    async def add_documents(self, folder_paths: List[str]) -> Dict[str, Any]:
        """Add documents from folders to the knowledge base."""
        async with self._processing_lock:  # Use lock to prevent race conditions
            if not self.initialized:
                await self.initialize()
            
            # Debug: Check vector store status
            print(f"🔍 Debug - Vector store status: {self.rag_app.vector_store_manager.vectorstore is not None}")
            
            # Double check that vector store is properly initialized
            if self.rag_app.vector_store_manager.vectorstore is None:
                print("⚠️ Vector store is None, attempting to re-initialize...")
                self.rag_app.setup_database(reset=False)
                if self.rag_app.vector_store_manager.vectorstore is None:
                    return {
                        "success": False,
                        "message": "Failed to initialize vector store"
                    }
            
            try:
                # Process documents
                start_time = time.time()
                
                # Use existing document ingestion
                self.rag_app.ingest_documents(folder_paths, web_urls=[])
                
                # Re-initialize RAG with new documents only if vector store is ready
                try:
                    if self.rag_app.vector_store_manager.vectorstore:
                        self.rag_app.initialize_rag()
                    else:
                        print("⚠️ Skipping RAG initialization - vector store not ready")
                except Exception as e:
                    print(f"⚠️ RAG initialization failed: {e}")
                
                processing_time = time.time() - start_time
                
                # Get statistics
                status = self.rag_app.get_system_status()
                doc_count = status.get('vector_store', {}).get('document_count', 0)
                
                return {
                    "success": True,
                    "message": f"Successfully processed documents from {len(folder_paths)} folders",
                    "statistics": {
                        "folders_processed": len(folder_paths),
                        "total_documents": doc_count,
                        "processing_time": round(processing_time, 2)
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to process documents: {str(e)}",
                    "error": str(e)
                }
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 10,
        similarity_threshold: float = 0.0
    ) -> SearchResponse:
        """Search for relevant documents."""
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Use RAG pipeline for search
            if self.rag_app.rag_pipeline.retriever is None:
                self.rag_app.initialize_rag()
            
            docs = self.rag_app.rag_pipeline.retrieve_documents(query)
            
            # Filter by limit and similarity threshold
            docs = docs[:limit]
            
            results = [
                SearchResult(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    score=getattr(doc, 'score', 1.0)
                )
                for doc in docs
                if getattr(doc, 'score', 1.0) >= similarity_threshold
            ]
            
            execution_time = time.time() - start_time
            
            return SearchResponse(
                results=results,
                total_results=len(results),
                query=query,
                execution_time=execution_time
            )
            
        except Exception as e:
            return SearchResponse(
                results=[],
                total_results=0,
                query=query,
                execution_time=time.time() - start_time
            )
    
    async def get_system_status(self) -> SystemStatus:
        """Get current system status."""
        if not self.initialized:
            return SystemStatus(
                status="not_initialized",
                components={},
                statistics={},
                last_updated=datetime.now()
            )
        
        try:
            # Get status from RAG app
            status = self.rag_app.get_system_status()
            
            components = {
                "database": {
                    "status": "healthy" if status.get('vector_store') else "error",
                    "documents": status.get('vector_store', {}).get('document_count', 0),
                    "path": self.settings.database.persist_directory
                },
                "models": {
                    "status": "healthy",
                    "embedding_model": self.settings.models.embedding_model,
                    "llm_model": self.settings.models.llm_model,
                    "available_models": status.get('available_models', [])
                },
                "processing": {
                    "status": "healthy",
                    "chunk_size": self.settings.processing.chunk_size,
                    "supported_formats": self.settings.processing.supported_extensions
                }
            }
            
            statistics = {
                "total_documents": status.get('vector_store', {}).get('document_count', 0),
                "uptime": "active",
                "last_query": "unknown"
            }
            
            return SystemStatus(
                status="healthy",
                components=components,
                statistics=statistics,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            return SystemStatus(
                status="error",
                components={"error": {"status": "error", "message": str(e)}},
                statistics={},
                last_updated=datetime.now()
            )
    
    async def update_configuration(
        self, 
        category: str, 
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update configuration dynamically."""
        try:
            if category == "database":
                for key, value in settings.items():
                    if hasattr(self.settings.database, key):
                        setattr(self.settings.database, key, value)
            elif category == "models":
                for key, value in settings.items():
                    if hasattr(self.settings.models, key):
                        setattr(self.settings.models, key, value)
            elif category == "processing":
                for key, value in settings.items():
                    if hasattr(self.settings.processing, key):
                        setattr(self.settings.processing, key, value)
            else:
                return {"success": False, "message": f"Unknown category: {category}"}
            
            # Re-initialize with new settings
            await self.initialize()
            
            return {
                "success": True,
                "message": f"Configuration updated for {category}",
                "updated_settings": settings
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update configuration: {str(e)}",
                "error": str(e)
            }
    
    def get_current_config(self, category: str) -> Dict[str, Any]:
        """Get current configuration for a category."""
        if category == "database":
            return {
                "persist_directory": self.settings.database.persist_directory,
                "collection_name": self.settings.database.collection_name
            }
        elif category == "models":
            return {
                "embedding_model": self.settings.models.embedding_model,
                "llm_model": self.settings.models.llm_model,
                "retriever_k": self.settings.models.retriever_k,
                "temperature": self.settings.models.temperature,
                "max_tokens": self.settings.models.max_tokens
            }
        elif category == "processing":
            return {
                "chunk_size": self.settings.processing.chunk_size,
                "chunk_overlap": self.settings.processing.chunk_overlap,
                "max_file_size_mb": self.settings.processing.max_file_size_mb,
                "supported_extensions": self.settings.processing.supported_extensions,
                "enable_ocr": self.settings.processing.enable_ocr,
                "ocr_languages": self.settings.processing.ocr_languages
            }
        else:
            return {}