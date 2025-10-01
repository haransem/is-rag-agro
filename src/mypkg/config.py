"""Configuration management for the RAG Agriculture system."""

import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """ChromaDB configuration."""
    persist_directory: str = "./chroma_db_nomic"
    collection_name: str = "agro_nomic_v1"
    chroma_db_impl: str = "duckdb+parquet"


@dataclass
class ModelConfig:
    """Model configuration for embeddings and LLM."""
    embedding_model: str = "nomic-embed-text"
    llm_model: str = "gemma3:27b"
    retriever_k: int = 5


@dataclass
class ProcessingConfig:
    """Document processing configuration."""
    chunk_size: int = 800
    chunk_overlap: int = 150
    separators: List[str] = None
    tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]


@dataclass
class AppConfig:
    """Main application configuration."""
    langchain_token: Optional[str] = None
    groq_token: Optional[str] = None
    database: DatabaseConfig = None
    model: ModelConfig = None
    processing: ProcessingConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.model is None:
            self.model = ModelConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()


def load_config() -> AppConfig:
    """Load configuration from environment variables and defaults."""
    load_dotenv()
    
    # Try to load from environment first, then use hardcoded values as fallback
    langchain_token = os.getenv("LC_TOKEN") or "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"
    groq_token = os.getenv("GROQ_TOKEN") or "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"
    
    # Set environment variables for LangSmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = langchain_token
    os.environ["GROQ_API_KEY"] = groq_token
    
    return AppConfig(
        langchain_token=langchain_token,
        groq_token=groq_token
    )
