"""
New Architecture Examples - Agriculture RAG System

This file demonstrates how to use the new FastAPI backend + Web frontend architecture.
"""

import asyncio
import sys
from pathlib import Path

# Add paths for legacy compatibility
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def example_api_usage():
    """Example of using the RAG system via API calls."""
    print("🌐 API Usage Examples")
    print("="*50)
    
    # Note: This would typically be done with requests or httpx in a real application
    # For demo purposes, we'll use the service directly
    
    from backend.app.core.config import get_settings
    from backend.app.services.rag_service import RAGService
    
    # Initialize service
    settings = get_settings()
    rag_service = RAGService(settings)
    
    # Initialize the service
    print("🔧 Initializing RAG service...")
    success = await rag_service.initialize()
    
    if not success:
        print("❌ Failed to initialize RAG service")
        return
    
    print("✅ RAG service initialized successfully")
    
    # Example 1: Process documents
    print("\n📚 Example 1: Processing Documents")
    folder_paths = ["./notebooks/Train/testing"]
    result = await rag_service.add_documents(folder_paths)
    print(f"📊 Processing result: {result}")
    
    # Example 2: Ask questions
    print("\n💬 Example 2: Asking Questions")
    questions = [
        "หลักสูตรเกษตรศาสตร์มีอะไรบ้าง",
        "วิธีการสมัครเรียนอย่างไร",
        "ค่าใช้จ่ายในการศึกษาเท่าไหร่"
    ]
    
    for question in questions:
        print(f"\n❓ คำถาม: {question}")
        response = await rag_service.process_question(
            question=question,
            include_sources=True,
            debug=False
        )
        print(f"🤖 คำตอบ: {response.answer[:200]}...")
        if response.sources:
            print(f"📑 แหล่งอ้างอิง: {len(response.sources)} เอกสาร")
    
    # Example 3: Search documents
    print("\n🔍 Example 3: Document Search")
    search_response = await rag_service.search_documents(
        query="เกษตรศาสตร์",
        limit=5,
        similarity_threshold=0.1
    )
    print(f"🔎 พบผลลัพธ์: {len(search_response.results)} รายการ")
    
    # Example 4: Get system status
    print("\n📊 Example 4: System Status")
    status = await rag_service.get_system_status()
    print(f"🟢 สถานะระบบ: {status.status}")
    print(f"📄 จำนวนเอกสาร: {status.statistics.get('total_documents', 0)}")
    
    # Example 5: Update configuration
    print("\n⚙️ Example 5: Configuration Update")
    config_result = await rag_service.update_configuration(
        "models",
        {"retriever_k": 3, "temperature": 0.2}
    )
    print(f"🔧 Configuration update: {config_result}")

async def example_configuration_scenarios():
    """Examples of different configuration scenarios."""
    print("\n🎛️ Configuration Scenarios")
    print("="*50)
    
    from backend.app.core.config import get_settings
    from backend.app.services.rag_service import RAGService
    
    settings = get_settings()
    rag_service = RAGService(settings)
    await rag_service.initialize()
    
    # Scenario 1: Fast responses (smaller model)
    print("\n⚡ Scenario 1: Fast Response Configuration")
    await rag_service.update_configuration("models", {
        "llm_model": "gemma3:8b",
        "retriever_k": 3,
        "temperature": 0.1
    })
    print("✅ Configured for fast responses")
    
    # Scenario 2: High quality (larger model)  
    print("\n🎯 Scenario 2: High Quality Configuration")
    await rag_service.update_configuration("models", {
        "llm_model": "gemma3:27b", 
        "retriever_k": 7,
        "temperature": 0.3
    })
    print("✅ Configured for high quality responses")
    
    # Scenario 3: Large documents (bigger chunks)
    print("\n📄 Scenario 3: Large Document Configuration")
    await rag_service.update_configuration("processing", {
        "chunk_size": 1200,
        "chunk_overlap": 200,
        "max_file_size_mb": 100
    })
    print("✅ Configured for large documents")
    
    # Show current configuration
    print("\n📋 Current Configuration:")
    for category in ["database", "models", "processing"]:
        config = rag_service.get_current_config(category)
        print(f"{category}: {config}")

def example_web_frontend():
    """Instructions for using the web frontend."""
    print("\n🌐 Web Frontend Usage")
    print("="*50)
    
    print("""
📋 To use the web interface:

1. 🚀 Start the server:
   cd backend
   python run_server.py

2. 🌐 Open browser:
   http://localhost:8000

3. 📑 Use the tabs:
   
   💬 Chat Tab:
   - Type questions in Thai or English
   - Toggle source documents
   - Enable debug mode for details
   
   📄 Documents Tab:
   - Drag & drop files to upload
   - Process entire folders
   - Monitor processing status
   
   🔍 Search Tab:
   - Search through documents
   - Adjust similarity threshold
   - Filter results
   
   ⚙️ Configuration Tab:
   - Change AI models in real-time
   - Adjust processing parameters
   - Reset to defaults
   
   📊 Status Tab:
   - Monitor system health
   - View performance metrics
   - Check available models

4. 🔧 Configuration Examples:
   
   Fast Mode:
   - LLM: gemma3:8b
   - Retriever K: 3
   - Temperature: 0.1
   
   Quality Mode:
   - LLM: gemma3:27b
   - Retriever K: 7
   - Temperature: 0.3
   
   Large Documents:
   - Chunk Size: 1200
   - Chunk Overlap: 200
   - Max File Size: 100MB
    """)

async def example_python_api_client():
    """Example of building a Python client for the API."""
    print("\n🐍 Python API Client Example")
    print("="*50)
    
    # This would be in a separate file/application
    api_example_code = '''
import requests
import json

class AgroRAGClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def ask_question(self, question, include_sources=True):
        """Ask a question to the RAG system."""
        response = requests.post(
            f"{self.api_url}/chat/ask",
            json={
                "question": question,
                "include_sources": include_sources,
                "debug": False
            }
        )
        return response.json()
    
    def upload_document(self, file_path):
        """Upload a document."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'process_immediately': True}
            response = requests.post(
                f"{self.api_url}/documents/upload",
                files=files,
                data=data
            )
        return response.json()
    
    def update_config(self, category, settings):
        """Update system configuration."""
        response = requests.put(
            f"{self.api_url}/config/{category}",
            json={"category": category, "settings": settings}
        )
        return response.json()
    
    def get_status(self):
        """Get system status."""
        response = requests.get(f"{self.api_url}/status/")
        return response.json()

# Usage example:
client = AgroRAGClient()

# Ask a question
result = client.ask_question("หลักสูตรเกษตรศาสตร์มีอะไรบ้าง")
print(f"Answer: {result['answer']}")

# Update configuration
client.update_config("models", {"llm_model": "gemma3:8b"})

# Check status
status = client.get_status()
print(f"System status: {status['status']}")
    '''
    
    print(api_example_code)

def comparison_with_legacy():
    """Show comparison between old and new architecture."""
    print("\n🔄 Legacy vs New Architecture")
    print("="*50)
    
    comparison = """
📊 Feature Comparison:

+------------------+------------------+------------------+
|     Feature      |      Legacy      |   New (v2.0)     |
+------------------+------------------+------------------+
| Interface        | Gradio only      | Web + API        |
| Configuration    | Code changes     | Runtime/UI       |
| Deployment       | Single process   | Scalable         |
| Integration      | Limited          | Full REST API    |
| Frontend         | Basic Gradio     | Modern HTML/CSS  |
| Mobile Support   | Limited          | Responsive       |
| Customization    | Hard             | Easy             |
| Documentation    | Basic            | Interactive      |
+------------------+------------------+------------------+

🔄 Migration Path:

1. Legacy code still works:
   python src/examples.py
   
2. Try new interface:
   python backend/run_server.py
   
3. Gradually move to API:
   Use REST endpoints for integration
   
4. Customize as needed:
   Modify frontend or add API endpoints

🎯 When to use which:

Legacy (src/mypkg):
✅ Quick scripts and automation
✅ Jupyter notebook development  
✅ Command-line usage

New Architecture (backend/frontend):
✅ Production web applications
✅ Integration with other systems
✅ Runtime configuration changes
✅ Team collaboration
✅ Scalable deployments
    """
    
    print(comparison)

async def main():
    """Run all examples."""
    print("🌾 Agriculture RAG System - New Architecture Examples")
    print("="*60)
    
    print("\n🎯 Available Examples:")
    print("1. API Usage (Programmatic)")
    print("2. Configuration Scenarios")  
    print("3. Web Frontend Guide")
    print("4. Python Client Example")
    print("5. Legacy Comparison")
    
    # Run examples
    try:
        await example_api_usage()
        await example_configuration_scenarios()
        example_web_frontend()
        await example_python_api_client()
        comparison_with_legacy()
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\n💡 To run examples properly:")
        print("1. Make sure dependencies are installed: pip install -r requirements.txt")
        print("2. Start Ollama service: ollama serve")
        print("3. Pull required models: ollama pull nomic-embed-text gemma3:27b")
        print("4. Add some documents to ./notebooks/Train/testing/")
    
    print(f"\n🎉 Examples completed!")
    print(f"🚀 Start the web server: cd backend && python run_server.py")
    print(f"🌐 Then visit: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main())