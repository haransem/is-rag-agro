"""Vector store management using ChromaDB."""

import shutil
import traceback
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document
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
        try:
            if reset:
                self.reset_database()
            
            # Initialize embeddings
            self.initialize_embeddings()
            print(f"🔧 Debug - Embeddings initialized: {self.embeddings is not None}")
            
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_config.persist_directory
            )
            print(f"🔧 Debug - ChromaDB client created: {self.chroma_client is not None}")
            
            # Create LangChain wrapper
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.db_config.collection_name,
                embedding_function=self.embeddings,
            )
            print(f"🔧 Debug - Vectorstore created: {self.vectorstore is not None}")
            
            # Validate the vector store is actually working
            if self.vectorstore:
                try:
                    # Test the connection
                    collection_count = len(self.chroma_client.list_collections())
                    print(f"🔧 Debug - ChromaDB has {collection_count} collections")
                    
                    # Additional debugging for object state
                    print(f"🔧 Debug - Vectorstore bool check: {bool(self.vectorstore)}")
                    print(f"🔧 Debug - Vectorstore _client type: {type(getattr(self.vectorstore, '_client', None))}")
                    print(f"🔧 Debug - Vectorstore _collection type: {type(getattr(self.vectorstore, '_collection', None))}")
                    
                except Exception as e:
                    print(f"⚠️ Warning - Vector store connection test failed: {e}")
                    print(f"⚠️ Error details: {traceback.format_exc()}")
            
            return self.vectorstore
            
        except Exception as e:
            print(f"❌ Error in setup_vectorstore: {e}")
            self.vectorstore = None
            raise
    
    def reset_database(self):
        """Reset/clear the ChromaDB database."""
        shutil.rmtree(self.db_config.persist_directory, ignore_errors=True)
        print(f"Reset database at: {self.db_config.persist_directory}")
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        print(f"🔍 Debug - add_documents called with {len(documents)} documents")
        
        # Simple direct approach - skip boolean checks, use None check only
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                print(f"🔧 Attempt {attempt + 1}: Processing documents...")
                
                # Re-initialize if vectorstore is None
                if self.vectorstore is None:
                    print("⚠️ Vector store is None, initializing...")
                    self.setup_vectorstore(reset=False)
                
                # Skip boolean check - directly try to use vectorstore
                if documents and self.vectorstore is not None:
                    print(f"📝 Adding {len(documents)} documents to vector store...")
                    self.vectorstore.add_documents(documents)
                    print("✅ Documents added successfully!")
                    return
                elif not documents:
                    print("⚠️ No documents to add")
                    return
                else:
                    print("⚠️ Vector store is None after initialization")
                    raise Exception("Vector store failed to initialize")
                    
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    print(f"❌ All attempts failed. Final error: {e}")
                    raise
                else:
                    print("🔄 Retrying with fresh vector store...")
                    self.vectorstore = None
                    self.setup_vectorstore(reset=False)
    
    def get_retriever(self, k: Optional[int] = None):
        """Get a retriever from the vector store."""
        # Try to re-initialize if vector store is None
        if not self.vectorstore:
            print("⚠️ Vector store is None in get_retriever, attempting to re-initialize...")
            try:
                self.setup_vectorstore(reset=False)
            except Exception as e:
                print(f"❌ Failed to re-initialize vector store: {e}")
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
