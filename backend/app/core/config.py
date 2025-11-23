"""Core configuration management."""

import os
from typing import List, Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    persist_directory: str = Field(default="./data/chroma_db", env="DB_PERSIST_DIR")
    collection_name: str = Field(default="agro_documents", env="DB_COLLECTION")
    

class ModelSettings(BaseSettings):
    """AI Model configuration."""
    embedding_model: str = Field(default="nomic-embed-text", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="gemma3:27b", env="LLM_MODEL")
    retriever_k: int = Field(default=5, env="RETRIEVER_K")
    temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")


class ProcessingSettings(BaseSettings):
    """Document processing configuration."""
    chunk_size: int = Field(default=800, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, env="CHUNK_OVERLAP")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    supported_extensions: List[str] = Field(
        default=[".pdf", ".docx", ".pptx", ".xlsx", ".csv", ".txt", ".jpg", ".png", ".jpeg", ".tiff", ".webp"],
        env="SUPPORTED_EXTENSIONS"
    )
    enable_ocr: bool = Field(default=True, env="ENABLE_OCR")
    ocr_languages: List[str] = Field(default=["tha", "eng"], env="OCR_LANGUAGES")


class APISettings(BaseSettings):
    """API configuration."""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    reload: bool = Field(default=False, env="API_RELOAD")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    

class Settings(BaseSettings):
    """Main application settings."""
    # Application
    app_name: str = "Agriculture RAG API"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Keys
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    
    # Components
    database: DatabaseSettings = DatabaseSettings()
    models: ModelSettings = ModelSettings()
    processing: ProcessingSettings = ProcessingSettings()
    api: APISettings = APISettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def update_settings(**kwargs) -> Settings:
    """Update settings dynamically."""
    global _settings
    if _settings is None:
        _settings = Settings()
    
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
        elif key.startswith('database_'):
            setattr(_settings.database, key.replace('database_', ''), value)
        elif key.startswith('models_'):
            setattr(_settings.models, key.replace('models_', ''), value)
        elif key.startswith('processing_'):
            setattr(_settings.processing, key.replace('processing_', ''), value)
            
    return _settings