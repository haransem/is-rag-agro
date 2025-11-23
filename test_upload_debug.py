#!/usr/bin/env python3
"""Simple test script to upload document and see debug output."""

import requests
import json
import time

def test_upload():
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Create test file content
    test_content = "Test agriculture document with farming information."
    
    try:
        # Make upload request
        print("📤 Uploading test document...")
        
        files = {'file': ('test_document.txt', test_content, 'text/plain')}
        data = {'process_immediately': 'true'}
        
        response = requests.post(
            'http://localhost:8000/api/v1/documents/upload',
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"📋 Response status: {response.status_code}")
        print(f"📋 Response body: {response.json()}")
        
    except Exception as e:
        print(f"❌ Error during upload: {e}")

if __name__ == "__main__":
    test_upload()