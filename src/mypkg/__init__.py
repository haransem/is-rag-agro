"""Agriculture RAG System - A comprehensive document processing and question-answering system."""

from .config import load_config, AppConfig, DatabaseConfig, ModelConfig, ProcessingConfig
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager
from .rag_pipeline import RAGPipeline
from .web_interface import WebInterface, create_simple_interface
from .main import AgroRAGApplication

__version__ = "1.0.0"
__author__ = "Agriculture RAG Team"

__all__ = [
    "load_config",
    "AppConfig",
    "DatabaseConfig", 
    "ModelConfig",
    "ProcessingConfig",
    "DocumentProcessor",
    "VectorStoreManager",
    "RAGPipeline",
    "WebInterface",
    "create_simple_interface",
    "AgroRAGApplication"
]
