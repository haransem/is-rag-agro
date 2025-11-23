"""API endpoints package."""

# Import routers to make them available
from . import chat, config, documents, status

__all__ = ["chat", "config", "documents", "status"]