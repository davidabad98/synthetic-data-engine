# app/context/request_context.py (recommended location)
"""
Request Context Holder Module

Provides a mechanism to store and access request-specific parameters throughout
the service layer without parameter threading.

Uses Context Variables (contextvars) for async-safe request isolation in FastAPI.
This is critical for proper concurrent request handling.

Typical usage:
- Set the context in your endpoint using the middleware or dependency
- Access anywhere in services using get_current_model()
"""

import logging
from contextvars import ContextVar
from typing import Optional

from config.config import DEFAULT_LLM

logger = logging.getLogger(__name__)
# Context variable storing the model for current request chain
selected_model_ctx: ContextVar[Optional[str]] = ContextVar("selected_model")


def get_current_model() -> str:
    """
    Safely retrieves the model from context with fallback to default

    Returns:
        str: Active model name or 'DEFAULT_LLM' if not set

    Raises:
        RuntimeError: If context not properly initialized
    """
    try:
        model = selected_model_ctx.get()
        if not model:
            raise LookupError
        return model
    except LookupError:
        logger.error("Current request context not set. Defaulting to {DEFAULT_LLM}")
        return DEFAULT_LLM  # Default fallback
