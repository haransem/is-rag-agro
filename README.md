# 🌾 Agriculture RAG System - Modern Web Architecture

A comprehensive document processing and question-answering system designed for agricultural knowledge management, featuring a **modern web frontend** and **RESTful API backend** with configurable RAG pipeline components.

## ✨ Features

- **🔍 Multi-format Document Processing**: PDF, DOCX, PPTX, XLSX, CSV, images, and web pages
- **🇹🇭 Thai Language Support**: Specialized OCR and text processing for Thai content  
- **🤖 Configurable RAG Pipeline**: Each step can be customized independently
- **🌐 Modern Web Interface**: React-like frontend with real-time configuration
- **📊 System Monitoring**: Real-time status and performance metrics
- **🔧 Modular Architecture**: Separate frontend/backend with REST API
- **⚙️ Dynamic Configuration**: Adjust models, processing, and database settings on-the-fly

## 🏗️ New Architecture

```
is-rag-agro/
├── 🎯 frontend/                 # Modern Web Frontend
│   ├── index.html              # Main application
│   └── static/
│       ├── css/style.css       # Responsive styling
│       └── js/
│           ├── api.js          # API client
│           └── app.js          # Frontend logic
├── 🚀 backend/                 # FastAPI Backend
│   └── app/
│       ├── main.py             # FastAPI application
│       ├── api/endpoints/      # REST API routes
│       │   ├── chat.py         # Q&A endpoints  
│       │   ├── config.py       # Configuration API
│       │   ├── documents.py    # Document management
│       │   └── status.py       # System monitoring
│       ├── services/
│       │   └── rag_service.py  # RAG business logic
│       ├── core/config.py      # Settings management
│       └── models/schemas.py   # Pydantic models
├── 📚 src/mypkg/              # Legacy RAG components (reused)
│   ├── document_processor.py  # Document processing
│   ├── vector_store.py        # ChromaDB operations  
│   ├── rag_pipeline.py        # RAG logic
│   └── config.py              # Configuration
└── 📝 notebooks/              # Jupyter examples
```

## 🚀 Quick Start Guide

### 📥 Step 1: Clone and Setup Environment

```bash
# 1. Clone the repository
git clone https://github.com/haransem/is-rag-agro.git
cd is-rag-agro

# 2. Create and activate virtual environment
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 🤖 Step 2: Install Ollama and AI Models

```bash
# 1. Install Ollama (if not installed)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Windows: Download from https://ollama.com

# 2. Start Ollama service
ollama serve

# 3. Download required models (in another terminal)
ollama pull nomic-embed-text     # Embedding model
ollama pull gemma2:9b           # LLM model (recommended)

# Alternative models (choose based on your hardware):
# ollama pull gemma2:2b          # Lighter model
# ollama pull gemma3:8b          # Balanced model
# ollama pull gemma3:27b         # High quality model
```

### 🏃‍♂️ Step 3: Start the Application

```bash
# Method 1: Quick start (recommended)
cd is-rag-agro
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the server with proper Python path
PYTHONPATH=/path/to/is-rag-agro:/path/to/is-rag-agro/backend uvicorn app.main:app --host 0.0.0.0 --port 8000

# Method 2: Alternative start (if above doesn't work)
cd backend
python -c "
import sys
sys.path.append('/path/to/is-rag-agro')
sys.path.append('/path/to/is-rag-agro/backend')
import uvicorn
from app.main import app
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### 🌐 Step 4: Access the Application

Once the server starts successfully, you'll see:
```
✅ RAG Service initialized
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**🔗 Access Points:**
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs  
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/status/health

### 📁 Step 5: Upload Documents and Start Using

#### Via Web Interface:
1. **Open browser** → http://localhost:8000
2. **Documents Tab** → Click "Choose Files" → Upload your documents
3. **Chat Tab** → Ask questions about your documents
4. **Configuration Tab** → Adjust AI models and settings

#### Via API:
```bash
# 1. Upload a document
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@/path/to/your/document.pdf" \
  -F "process_immediately=true"

# 2. Ask a question
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "หลักสูตรเกษตรศาสตร์มีอะไรบ้าง", 
    "include_sources": true
  }'

# 3. Search documents
curl -X POST "http://localhost:8000/api/v1/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "การเกษตรยั่งยืน",
    "limit": 5
  }'

# 4. Check system status
curl "http://localhost:8000/api/v1/status/health"
```

### ⚡ Step 6: Configuration and Optimization

#### Change AI Models via API:
```bash
# Switch to faster model
curl -X PUT "http://localhost:8000/api/v1/config/models" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_model": "gemma2:2b",
    "embedding_model": "nomic-embed-text",
    "retriever_k": 5,
    "temperature": 0.3
  }'

# Switch to high-quality model
curl -X PUT "http://localhost:8000/api/v1/config/models" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_model": "gemma3:27b",
    "retriever_k": 10,
    "temperature": 0.1
  }'
```

#### Adjust Processing Settings:
```bash
curl -X PUT "http://localhost:8000/api/v1/config/processing" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 800,
    "chunk_overlap": 150,
    "max_file_size_mb": 50
  }'
```

### 🔧 Troubleshooting Common Issues

#### Issue 1: Import Errors
```bash
# Solution: Set Python path correctly
export PYTHONPATH="${PYTHONPATH}:/full/path/to/is-rag-agro:/full/path/to/is-rag-agro/backend"

# Or use absolute path
cd /full/path/to/is-rag-agro
PYTHONPATH=$(pwd):$(pwd)/backend uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Issue 2: Ollama Connection Error
```bash
# Check Ollama is running
ollama list

# Start Ollama service
ollama serve

# Test model availability
ollama show nomic-embed-text
ollama show gemma2:9b
```

#### Issue 3: Vector Store Initialization Failed
```bash
# Clear vector database and restart
rm -rf data/chroma_db
rm -rf notebooks/chroma_db_nomic

# Restart server
```

#### Issue 4: Port Already in Use
```bash
# Use different port
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Or kill existing process
pkill -f uvicorn
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

### 📊 Step 7: Monitoring and Usage

#### Check System Health:
```bash
curl "http://localhost:8000/api/v1/status/health" | jq '.'
```

#### View Available Models:
```bash
curl "http://localhost:8000/api/v1/status/models" | jq '.'
```

#### Monitor Performance:
```bash
curl "http://localhost:8000/api/v1/status/statistics" | jq '.'
```

### 🎯 Web Interface Features

#### 💬 Chat Tab
- **Real-time Q&A**: Ask questions and get AI responses
- **Source Citations**: View which documents were used
- **Conversation History**: Keep track of your questions

#### 📄 Documents Tab  
- **File Upload**: Drag & drop or browse files
- **Bulk Processing**: Upload multiple files at once
- **Format Support**: PDF, DOCX, PPTX, XLSX, CSV, Images
- **Processing Status**: Real-time upload and processing feedback

#### 🔍 Search Tab
- **Semantic Search**: Find relevant documents
- **Similarity Scoring**: See relevance scores
- **Filter Results**: Limit results by relevance threshold

#### ⚙️ Configuration Tab
- **Model Selection**: Change AI models on-the-fly
- **Processing Settings**: Adjust chunk size, overlap
- **Database Settings**: Configure storage options
- **Performance Tuning**: Temperature, retrieval settings

#### 📊 Status Tab
- **System Health**: Real-time monitoring
- **Database Statistics**: Document counts, sizes
- **Model Information**: Currently loaded models
- **Performance Metrics**: Response times, usage stats

## 🎛️ Configuration System

The new architecture allows **real-time configuration** of every RAG component:

### 📊 Database Configuration
- **Collection Name**: Name your document collections
- **Storage Path**: Configure where data is stored
- **Database Backend**: Choose storage implementation

### 🧠 AI Model Configuration  
- **Embedding Model**: `nomic-embed-text`, `mxbai-embed-large`
- **LLM Model**: `gemma3:27b`, `gemma3:8b`, `llama3:8b`
- **Retriever Settings**: Number of documents to retrieve (K)
- **Generation Settings**: Temperature, max tokens

### ⚙️ Processing Configuration
- **Chunk Size**: Size of text chunks (200-2000 characters)
- **Chunk Overlap**: Overlap between chunks (50-500 characters) 
- **File Size Limits**: Maximum upload size
- **OCR Settings**: Languages and processing options

### 🔄 Runtime Reconfiguration

```python
# Via API
import requests

# Change to smaller model for faster responses
config_update = {
    "category": "models", 
    "settings": {
        "llm_model": "gemma3:8b",
        "retriever_k": 3
    }
}

response = requests.put(
    "http://localhost:8000/api/v1/config/models",
    json=config_update
)
```

## 📡 API Reference

### Chat Endpoints
- `POST /api/v1/chat/ask` - Ask questions
- `GET /api/v1/chat/conversations/{id}` - Get chat history

### Document Endpoints  
- `POST /api/v1/documents/upload` - Upload files
- `POST /api/v1/documents/bulk-process` - Process folders
- `POST /api/v1/documents/search` - Search documents

### Configuration Endpoints
- `GET /api/v1/config/{category}` - Get current config
- `PUT /api/v1/config/{category}` - Update config  
- `POST /api/v1/config/reset/{category}` - Reset to defaults

### Status Endpoints
- `GET /api/v1/status/` - System status
- `GET /api/v1/status/models` - Available AI models
- `GET /api/v1/status/statistics` - Usage statistics

## 💻 Development

### Backend Development

```bash
# Install with development dependencies
pip install -r requirements.txt

# Start with hot reload
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest backend/tests/

# API documentation
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

### Frontend Development

The frontend is pure HTML/CSS/JavaScript - no build process required:

```bash
# Frontend files are in /frontend/
# Edit frontend/static/js/app.js for logic
# Edit frontend/static/css/style.css for styling
# Changes are reflected immediately (browser refresh)
```

### Adding New Features

1. **New API Endpoint**: Add to `backend/app/api/endpoints/`
2. **New Configuration**: Update `backend/app/core/config.py`  
3. **Frontend UI**: Modify `frontend/static/js/app.js`
4. **Business Logic**: Extend `backend/app/services/rag_service.py`

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker build -t agriculture-rag .
docker run -p 8000:8000 -v $(pwd)/data:/app/data agriculture-rag

# Or use docker-compose (if provided)
docker-compose up -d
```

## 🔄 Migration from Legacy

If you have the old Gradio-based system:

```bash
# Your old code still works!
python src/examples.py

# But try the new web interface:
python backend/run_server.py
```

### Key Improvements

| Legacy | New Architecture | Benefits |
|--------|-----------------|----------|
| Single Gradio app | Frontend + Backend API | Better separation of concerns |
| Fixed configuration | Runtime configuration | No restart needed for changes |
| Limited scalability | REST API | Can scale horizontally |
| Basic UI | Modern responsive web | Better user experience |
| No API access | Full REST API | Integration with other systems |

## 📊 Performance & Scaling

### Hardware Recommendations

| Component | Minimum | Recommended | High Performance |
|-----------|---------|-------------|------------------|
| **RAM** | 8GB | 16GB | 32GB+ |
| **Storage** | 20GB SSD | 100GB SSD | 500GB+ NVMe |
| **CPU** | 4 cores | 8 cores | 16+ cores |
| **GPU** | None | 8GB VRAM | 16GB+ VRAM |

### Model Selection Guide

```bash
# For development/testing (fast, less accurate)
ollama pull gemma:2b

# For production (balanced)  
ollama pull gemma3:8b

# For high quality (slower, more accurate)
ollama pull gemma3:27b
ollama pull llama3.2:70b
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
