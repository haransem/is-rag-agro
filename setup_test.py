"""Setup and test script for the refactored Agriculture RAG System."""

import sys
import os
from pathlib import Path

def setup_and_test():
    """Setup and test the refactored system."""
    print("🌾 Agriculture RAG System - Setup and Test")
    print("=" * 50)
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from mypkg import AgroRAGApplication
        from mypkg.config import load_config
        print("✅ All imports successful")
        
        # Initialize application
        print("\n🔧 Initializing application...")
        app = AgroRAGApplication()
        print("✅ Application initialized")
        
        # Show configuration
        print(f"✅ Configuration loaded:")
        print(f"  - Embedding model: {app.config.model.embedding_model}")
        print(f"  - LLM model: {app.config.model.llm_model}")
        print(f"  - Database: {app.config.database.persist_directory}")
        
        # Check if training data exists
        train_folder = Path("notebooks/Train/testing")
        if train_folder.exists():
            files = list(train_folder.glob("*"))
            print(f"✅ Training data found: {len(files)} files")
            
            # Test document processing (without full pipeline)
            print("\n📚 Testing document processor...")
            processor = app.document_processor
            print("✅ Document processor ready")
            
        else:
            print("⚠️  No training data found - add documents to notebooks/Train/testing/")
        
        print(f"\n🎉 Setup complete! The refactored system is ready.")
        print(f"\n🚀 To run the full system:")
        print(f"   1. Add documents to: notebooks/Train/testing/")
        print(f"   2. Run: python src/examples.py")
        print(f"   3. Or use the Jupyter notebook: notebooks/refactored_demo.ipynb")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

if __name__ == "__main__":
    success = setup_and_test()
    sys.exit(0 if success else 1)
