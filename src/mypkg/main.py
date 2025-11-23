"""Main application orchestration."""

import os
import sys
from typing import List, Optional

from .config import load_config, AppConfig
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager
from .rag_pipeline import RAGPipeline
from .web_interface import WebInterface, create_simple_interface


class AgroRAGApplication:
    """Main application class that orchestrates all components."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config()
        self.document_processor = None
        self.vector_store_manager = None
        self.rag_pipeline = None
        self.web_interface = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all application components."""
        # Document processor
        self.document_processor = DocumentProcessor(self.config.processing)
        
        # Vector store manager
        self.vector_store_manager = VectorStoreManager(
            self.config.database,
            self.config.model
        )
        
        # RAG pipeline
        self.rag_pipeline = RAGPipeline(
            self.vector_store_manager,
            self.config.model
        )
        
        # Web interface
        self.web_interface = WebInterface(self.rag_pipeline)
    
    def setup_database(self, reset: bool = False):
        """Set up the vector database."""
        print("🔧 Setting up vector database...")
        self.vector_store_manager.setup_vectorstore(reset=reset)
        print("✅ Vector database ready")
        
        return self
    
    def ingest_documents(self, folder_paths: List[str], web_urls: Optional[List[str]] = None):
        """Ingest documents from folders and web URLs."""
        print("📚 Starting document ingestion...")
        
        # Load documents from folders
        docs = self.document_processor.load_documents_from_folders(folder_paths)
        
        # Load web pages if provided
        if web_urls:
            print(f"🌐 Loading {len(web_urls)} web pages...")
            for url in web_urls:
                try:
                    web_docs = self.document_processor.load_web_page(url)
                    docs.extend(web_docs)
                    print(f"✅ Loaded: {url}")
                except Exception as e:
                    print(f"❌ Failed to load {url}: {e}")
        
        # Process documents for vector store
        splits = self.document_processor.process_documents_for_vector_store(docs)
        
        # Add to vector store with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ensure vector store is still initialized
                if not self.vector_store_manager.vectorstore:
                    print(f"⚠️ Vector store lost during processing (attempt {attempt + 1}), re-initializing...")
                    self.vector_store_manager.setup_vectorstore(reset=False)
                
                # Try to add documents
                self.vector_store_manager.add_documents(splits)
                break  # Success, exit retry loop
            
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                # Reset and retry
                print("🔄 Resetting vector store and retrying...")
                self.vector_store_manager.setup_vectorstore(reset=False)
        
        print(f"✅ Ingestion complete: {len(docs)} raw docs → {len(splits)} chunks")
        
        return self
    
    def initialize_rag(self):
        """Initialize the RAG pipeline."""
        print("🤖 Initializing RAG pipeline...")
        self.rag_pipeline.initialize()
        print("✅ RAG pipeline ready")
        
        return self
    
    def query(self, question: str, debug: bool = False) -> str:
        """Query the RAG system."""
        return self.rag_pipeline.query(question, debug=debug)
    
    def start_web_interface(self, simple: bool = False, share: bool = False):
        """Start the web interface."""
        if simple:
            interface = create_simple_interface(self.rag_pipeline)
            return interface.launch(share=share)
        else:
            return self.web_interface.launch(share=share)
    
    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        status = {
            "config": {
                "embedding_model": self.config.model.embedding_model,
                "llm_model": self.config.model.llm_model,
                "database_path": self.config.database.persist_directory,
                "collection_name": self.config.database.collection_name,
            },
            "vector_store": self.vector_store_manager.get_collection_info(),
            "available_models": self._get_available_ollama_models(),
        }
        
        return status
    
    def _get_available_ollama_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            import ollama
            models = ollama.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            return [f"Error getting models: {e}"]
    
    def reset_database(self):
        """Reset the vector database."""
        print("🗑️ Resetting database...")
        self.vector_store_manager.reset_database()
        print("✅ Database reset complete")
        
        return self
    
    def run_full_pipeline(self, folder_paths: List[str], web_urls: Optional[List[str]] = None, 
                         reset_db: bool = True, start_web: bool = True, simple_web: bool = False):
        """Run the complete pipeline from setup to web interface."""
        try:
            # Setup
            self.setup_database(reset=reset_db)
            
            # Ingest
            self.ingest_documents(folder_paths, web_urls)
            
            # Initialize RAG
            self.initialize_rag()
            
            # Print status
            status = self.get_system_status()
            print("\n📊 System Status:")
            print(f"  Database: {status['vector_store'].get('document_count', 'Unknown')} documents")
            print(f"  Embedding Model: {status['config']['embedding_model']}")
            print(f"  LLM Model: {status['config']['llm_model']}")
            
            # Start web interface
            if start_web:
                print("\n🌐 Starting web interface...")
                return self.start_web_interface(simple=simple_web)
            
            return self
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            raise


def main():
    """Main entry point for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agro RAG System")
    parser.add_argument("--folders", nargs="+", required=True,
                       help="Folders containing documents to ingest")
    parser.add_argument("--urls", nargs="*", 
                       help="Web URLs to ingest")
    parser.add_argument("--no-reset", action="store_true",
                       help="Don't reset database before ingestion")
    parser.add_argument("--no-web", action="store_true",
                       help="Don't start web interface")
    parser.add_argument("--simple-web", action="store_true",
                       help="Use simple web interface")
    parser.add_argument("--query", type=str,
                       help="Single query to run (no web interface)")
    
    args = parser.parse_args()
    
    # Initialize application
    app = AgroRAGApplication()
    
    if args.query:
        # Single query mode
        app.setup_database(reset=not args.no_reset)
        if not args.no_reset:  # Only ingest if not preserving existing data
            app.ingest_documents(args.folders, args.urls)
        app.initialize_rag()
        
        result = app.query(args.query, debug=True)
        print(f"\nQ: {args.query}")
        print(f"A: {result}")
    else:
        # Full pipeline mode
        app.run_full_pipeline(
            folder_paths=args.folders,
            web_urls=args.urls,
            reset_db=not args.no_reset,
            start_web=not args.no_web,
            simple_web=args.simple_web
        )


if __name__ == "__main__":
    main()
