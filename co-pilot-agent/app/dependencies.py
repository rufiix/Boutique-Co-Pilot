"""FastAPI dependency injection container.

Provides singleton-scoped service instances to route handlers via
FastAPI's ``Depends`` mechanism. Centralizes object graph construction
to enforce the Dependency Inversion Principle.
"""

from __future__ import annotations

import functools

from app.config import Settings, get_settings
from app.services.context import ContextManager
from app.services.copilot import CoPilotService
from app.services.llm import LLMClient, VertexAIClient

_context_manager: ContextManager = ContextManager()


@functools.lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    """Return a cached LLM client instance.

    Returns:
        A singleton :class:`VertexAIClient`.
    """
    settings: Settings = get_settings()
    return VertexAIClient(settings)


def get_context_manager() -> ContextManager:
    """Return the application-scoped context manager.

    Returns:
        The shared :class:`ContextManager` instance.
    """
    return _context_manager


def get_copilot_service() -> CoPilotService:
    """Construct a CoPilotService with injected dependencies.

    Returns:
        A :class:`CoPilotService` wired to the LLM client and
        context manager.
    """
    return CoPilotService(
        llm_client=get_llm_client(),
        context_manager=get_context_manager(),
    )
