#!/usr/bin/env python3
"""
Agriculture RAG Backend Server Startup Script
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All required dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server."""
    if not check_dependencies():
        return False
    
    print("🚀 Starting Agriculture RAG Backend Server...")
    print("🌐 Frontend will be served at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("🔧 Admin interface: http://localhost:8000/redoc")
    print("\n" + "="*50)
    
    try:
        # Start the server using string reference for reload support
        import uvicorn
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)