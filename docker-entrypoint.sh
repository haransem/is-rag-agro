#!/bin/bash

# Start Ollama service in the background
ollama serve &

# Wait for Ollama to be ready
sleep 5

# Pull required models
ollama pull nomic-embed-text
ollama pull gemma3:27b

# Start the FastAPI application
cd /app/backend
python run_server.py