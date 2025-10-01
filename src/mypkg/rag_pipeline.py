"""RAG pipeline for question answering."""

from typing import List, Dict, Any, Optional
import ollama
from langchain.schema import Document

from .config import ModelConfig
from .vector_store import VectorStoreManager


class RAGPipeline:
    """Main RAG pipeline for processing queries and generating responses."""
    
    def __init__(self, vector_store_manager: VectorStoreManager, model_config: ModelConfig):
        self.vector_store_manager = vector_store_manager
        self.model_config = model_config
        self.retriever = None
        
    def initialize(self):
        """Initialize the RAG pipeline."""
        self.retriever = self.vector_store_manager.get_retriever()
        return self
    
    def retrieve_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents for a query."""
        if not self.retriever:
            raise ValueError("RAG pipeline not initialized. Call initialize() first.")
        
        try:
            # Support both new and old LangChain APIs
            return self.retriever.invoke(query)
        except Exception:
            return self.retriever.get_relevant_documents(query)
    
    def generate_context(self, documents: List[Document]) -> str:
        """Generate context string from retrieved documents."""
        return "\n\n".join(doc.page_content for doc in documents)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using Ollama LLM."""
        prompt = self._create_prompt(query, context)
        
        try:
            response = ollama.chat(
                model=self.model_config.llm_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Error generating response: {e}"
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create a well-formatted prompt for the LLM."""
        guardrail = (
            "คุณเป็นผู้ช่วยตอบคำถามจากฐานข้อมูลเท่านั้น "
            "ให้ใช้ข้อมูลที่อยู่ใน 'เนื้อหา (Context)' ด้านล่างเท่านั้นในการตอบ "
            "ห้ามเติมความรู้ภายนอกหรือคาดเดาเอง "
            "ถ้าไม่พบคำตอบใน Context ให้ตอบว่า: \"ไม่พบข้อมูลในฐานข้อมูลสำหรับคำถามนี้\".\n\n"
            "รูปแบบคำตอบ: ตอบสั้น กระชับ เป็นข้อ ๆ (ถ้าเหมาะสม) และแนบอ้างอิงท้ายบรรทัดเช่น [1],[2]\n"
        )
        
        return f"""{guardrail}
คำถาม: {query}

เนื้อหา (Context):
{context}

โปรดตอบเป็นภาษาไทย สรุปข้อเท็จจริงสำคัญ กระชับ ชัดเจน
"""
    
    def query(self, question: str, debug: bool = False) -> str:
        """Process a complete query through the RAG pipeline."""
        try:
            # Retrieve documents
            docs = self.retrieve_documents(question)
            
            if debug:
                self._print_debug_info(question, docs)
            
            # Generate context and response
            context = self.generate_context(docs)
            response = self.generate_response(question, context)
            
            return response
            
        except Exception as e:
            return f"Error processing query: {e}"
    
    def _print_debug_info(self, query: str, docs: List[Document]):
        """Print debug information about retrieved documents."""
        print(f"🔎 Query: {query}")
        print(f"📌 Retrieved {len(docs)} documents:\n")

        for i, doc in enumerate(docs, 1):
            print(f"--- Document {i} ---")
            print("Meta:", doc.metadata)
            print("Content:", doc.page_content[:300], "...\n")
    
    def get_similar_documents(self, query: str, k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get similar documents with metadata for analysis."""
        docs = self.vector_store_manager.similarity_search(query, k)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            }
            for doc in docs
        ]
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, str]]:
        """Process multiple questions in batch."""
        results = []
        
        for question in questions:
            try:
                answer = self.query(question)
                results.append({
                    "question": question,
                    "answer": answer,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "question": question,
                    "answer": f"Error: {e}",
                    "status": "error"
                })
        
        return results
