# 🌾 Agriculture RAG System - Refactored

A comprehensive document processing and question-answering system designed for agricultural knowledge management, built with modern modular architecture.

## ✨ Features

- **🔍 Multi-format Document Processing**: PDF, DOCX, PPTX, XLSX, CSV, images, and web pages
- **🇹🇭 Thai Language Support**: Specialized OCR and text processing for Thai content
- **🤖 RAG Pipeline**: Retrieval-Augmented Generation with ChromaDB and Ollama
- **🌐 Web Interface**: Interactive Gradio-based UI with multiple tabs
- **📊 System Monitoring**: Real-time status and document management
- **🔧 Modular Architecture**: Clean, maintainable, and extensible codebase

## 🏗️ Architecture

```
src/mypkg/
├── config.py              # Configuration management
├── text_processing.py     # Thai text processing utilities
├── document_processor.py  # Document loading and processing
├── vector_store.py        # ChromaDB operations
├── rag_pipeline.py        # Query processing and response generation
├── web_interface.py       # Gradio UI components
├── main.py                # Application orchestration
└── __init__.py            # Package initialization
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama models
ollama pull nomic-embed-text
ollama pull gemma3:27b
```

### 2. Basic Usage

```python
from mypkg import AgroRAGApplication

# Initialize application
app = AgroRAGApplication()

# Run complete pipeline
app.run_full_pipeline(
    folder_paths=['./Train/testing'],
    web_urls=[],  # Optional web URLs
    reset_db=True,
    start_web=True
)
```

### 3. Step-by-Step Usage

```python
# Initialize
app = AgroRAGApplication()

# Setup database
app.setup_database(reset=True)

# Ingest documents
app.ingest_documents(['./data/documents'])

# Initialize RAG
app.initialize_rag()

# Query the system
answer = app.query("หลักสูตรเกษตรศาสตร์มีอะไรบ้าง")
print(answer)

# Start web interface
app.start_web_interface()
```

## 📋 Usage Examples

### Command Line Interface

```bash
# Basic usage
python -m mypkg.main --folders ./data/docs --urls https://example.com

# Single query mode
python -m mypkg.main --folders ./data/docs --query "หลักสูตรเกษตรศาสตร์คืออะไร"

# Preserve existing database
python -m mypkg.main --folders ./data/docs --no-reset

# Simple web interface
python -m mypkg.main --folders ./data/docs --simple-web
```

### Jupyter Notebook

See `notebooks/refactored_demo.ipynb` for detailed examples.

### Programmatic Usage

```python
# Batch processing
questions = ["คำถาม 1", "คำถาม 2", "คำถาม 3"]
results = app.rag_pipeline.batch_query(questions)

# Document search
similar_docs = app.rag_pipeline.get_similar_documents("เกษตร", k=5)

# System status
status = app.get_system_status()
print(f"Documents: {status['vector_store']['document_count']}")
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
LC_TOKEN=your_langchain_token
GROQ_TOKEN=your_groq_token
```

### Custom Configuration

```python
from mypkg.config import AppConfig, DatabaseConfig, ModelConfig

config = AppConfig(
    database=DatabaseConfig(
        persist_directory="./custom_db",
        collection_name="my_collection"
    ),
    model=ModelConfig(
        embedding_model="mxbai-embed-large",
        llm_model="llama3:8b",
        retriever_k=10
    )
)
```

## 🌐 Web Interface

The system provides two web interface options:

### Advanced Interface (Default)
- **💬 Q&A Tab**: Interactive question-answering
- **🔍 Search Tab**: Document similarity search
- **📊 System Info Tab**: Database statistics and monitoring

### Simple Interface
- Backward-compatible single-page interface
- Minimal UI for basic Q&A functionality

## 📁 Supported File Formats

| Format | Description | Features |
|--------|-------------|----------|
| PDF | Portable Document Format | OCR, table extraction, multi-language |
| DOCX | Microsoft Word | Text extraction, metadata |
| PPTX | Microsoft PowerPoint | Slide content, images |
| XLSX | Microsoft Excel | Table data, formulas |
| CSV | Comma-separated values | Structured data |
| Images | JPG, PNG, WEBP, TIFF | OCR with Thai/English support |
| Web Pages | HTML content | Text + image OCR |

## 🇹🇭 Thai Language Processing

The system includes specialized Thai language processing:

- **OCR Error Correction**: Fixes common Thai OCR spacing issues
- **Word Tokenization**: Uses PyThaiNLP for accurate tokenization  
- **Unicode Normalization**: Handles Thai character encoding properly
- **Mixed Language Support**: Thai and English in the same documents

## 🔧 System Requirements

### Hardware
- **RAM**: 8GB+ recommended
- **Storage**: 2GB+ for models and databases
- **GPU**: Optional, CUDA-compatible for faster processing

### Software
- **Python**: 3.8+
- **Ollama**: For LLM and embedding models
- **Tesseract**: For OCR functionality

### Installation Notes

```bash
# Windows: Install Tesseract
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Update tesseract path in config if needed
# Default: C:\Program Files\Tesseract-OCR\tesseract.exe
```

## 🧪 Testing

```bash
# Run the demo notebook
jupyter notebook notebooks/refactored_demo.ipynb

# Test individual components
python src/examples.py

# Command line test
python -m mypkg.main --folders ./test_data --query "test question"
```

## 🔄 Migration from Original Code

If you have the original monolithic notebook code:

1. **Extract your data folders** and update paths in the new system
2. **Copy your `.env` file** or update configuration
3. **Install new requirements**: `pip install -r requirements.txt`
4. **Run the migration**: Use the new `AgroRAGApplication` class

### Key Changes
- **Modular structure**: Code split into logical components
- **Configuration management**: Centralized config system
- **Better error handling**: Robust error management
- **Type hints**: Improved code documentation
- **Web interface**: Enhanced UI with multiple tabs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes in the appropriate module
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the `notebooks/refactored_demo.ipynb` for examples
2. Review the configuration in `src/mypkg/config.py`
3. Check system requirements and dependencies
4. Create an issue with detailed error information

---

**🎯 Built for agricultural knowledge management with modern Python practices**
