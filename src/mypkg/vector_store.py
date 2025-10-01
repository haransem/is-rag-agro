"""Vector store management using ChromaDB."""

import shutil
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

# Use the newer package to reduce deprecation warnings
try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings

from .config import DatabaseConfig, ModelConfig


class VectorStoreManager:
    """Manages ChromaDB vector store operations."""
    
    def __init__(self, db_config: DatabaseConfig, model_config: ModelConfig):
        self.db_config = db_config
        self.model_config = model_config
        self.embeddings = None
        self.vectorstore = None
        self.chroma_client = None
        
    def initialize_embeddings(self):
        """Initialize embedding model."""
        if self.embeddings is None:
            self.embeddings = OllamaEmbeddings(model=self.model_config.embedding_model)
        return self.embeddings
    
    def setup_vectorstore(self, reset: bool = False):
        """Set up ChromaDB vector store."""
        if reset:
            self.reset_database()
        
        # Initialize embeddings
        self.initialize_embeddings()
        
        # Create ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=self.db_config.persist_directory
        )
        
        # Create LangChain wrapper
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.db_config.collection_name,
            embedding_function=self.embeddings,
        )
        
        return self.vectorstore
    
    def reset_database(self):
        """Reset/clear the ChromaDB database."""
        shutil.rmtree(self.db_config.persist_directory, ignore_errors=True)
        print(f"Reset database at: {self.db_config.persist_directory}")
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call setup_vectorstore() first.")
        
        if not documents:
            print("Warning: No documents to add")
            return
        
        print(f"Adding {len(documents)} documents to vector store...")
        self.vectorstore.add_documents(documents)
        print("Documents added successfully")
    
    def get_retriever(self, k: Optional[int] = None):
        """Get a retriever from the vector store."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call setup_vectorstore() first.")
        
        search_k = k or self.model_config.retriever_k
        return self.vectorstore.as_retriever(search_kwargs={"k": search_k})
    
    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Perform similarity search."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call setup_vectorstore() first.")
        
        search_k = k or self.model_config.retriever_k
        return self.vectorstore.similarity_search(query, k=search_k)
    
    def get_collection_info(self) -> dict:
        """Get information about the current collection."""
        if not self.chroma_client:
            return {"error": "ChromaDB client not initialized"}
        
        try:
            collection = self.chroma_client.get_collection(self.db_config.collection_name)
            return {
                "collection_name": self.db_config.collection_name,
                "document_count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception as e:
            return {"error": f"Failed to get collection info: {e}"}
    
    def delete_collection(self):
        """Delete the current collection."""
        if not self.chroma_client:
            raise ValueError("ChromaDB client not initialized")
        
        try:
            self.chroma_client.delete_collection(self.db_config.collection_name)
            print(f"Deleted collection: {self.db_config.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def list_collections(self) -> List[str]:
        """List all available collections."""
        if not self.chroma_client:
            return []
        
        try:
            collections = self.chroma_client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
