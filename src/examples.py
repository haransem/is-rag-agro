"""Usage examples for the refactored Agriculture RAG System."""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mypkg import AgroRAGApplication


def example_basic_usage():
    """Basic usage example."""
    # Initialize the application
    app = AgroRAGApplication()
    
    # Define data folders
    folder_paths = ['./Train/testing']  # Your document folders
    web_urls = [
        # "https://registrar.ku.ac.th/calendar",
        # "https://agro.ku.ac.th/th/academics",
    ]
    
    # Run the complete pipeline
    app.run_full_pipeline(
        folder_paths=folder_paths,
        web_urls=web_urls,
        reset_db=True,  # Reset database
        start_web=True,  # Start web interface
        simple_web=False  # Use advanced interface
    )


def example_step_by_step():
    """Step-by-step usage example."""
    # Initialize
    app = AgroRAGApplication()
    
    # Setup database
    app.setup_database(reset=True)
    
    # Ingest documents
    folder_paths = ['./Train/testing']
    app.ingest_documents(folder_paths)
    
    # Initialize RAG
    app.initialize_rag()
    
    # Test some queries
    questions = [
        "หลักสูตรเกษตรศาสตร์มีอะไรบ้าง",
        "วิธีการสมัครเรียน",
        "ค่าใช้จ่ายในการศึกษา"
    ]
    
    for question in questions:
        answer = app.query(question, debug=True)
        print(f"Q: {question}")
        print(f"A: {answer}")
        print("-" * 50)
    
    # Start web interface
    app.start_web_interface(simple=False)


def example_programmatic_queries():
    """Example for programmatic usage without web interface."""
    app = AgroRAGApplication()
    
    # Setup and ingest
    app.setup_database(reset=True)
    app.ingest_documents(['./Train/testing'])
    app.initialize_rag()
    
    # Batch queries
    questions = [
        "หลักสูตรเกษตรศาสตร์คืออะไร",
        "การสมัครเรียนต้องทำอย่างไร",
        "มีวิชาอะไรบ้างในหลักสูตร"
    ]
    
    results = app.rag_pipeline.batch_query(questions)
    
    for result in results:
        print(f"Q: {result['question']}")
        print(f"A: {result['answer']}")
        print(f"Status: {result['status']}")
        print("-" * 50)


def example_custom_configuration():
    """Example with custom configuration."""
    from mypkg.config import AppConfig, DatabaseConfig, ModelConfig, ProcessingConfig
    
    # Custom configuration
    config = AppConfig(
        database=DatabaseConfig(
            persist_directory="./custom_db",
            collection_name="custom_collection"
        ),
        model=ModelConfig(
            embedding_model="mxbai-embed-large",  # Different embedding model
            llm_model="llama3:8b",  # Different LLM
            retriever_k=10  # More results
        ),
        processing=ProcessingConfig(
            chunk_size=1000,  # Larger chunks
            chunk_overlap=200  # More overlap
        )
    )
    
    # Use custom config (you'd need to modify the constructor to accept config)
    # app = AgroRAGApplication(config=config)


if __name__ == "__main__":
    # Run the basic example
    print("Running basic usage example...")
    example_basic_usage()
