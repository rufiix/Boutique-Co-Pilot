"""Shared pytest fixtures for the Co-Pilot Agent test suite."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_context_manager, get_copilot_service, get_llm_client
from app.main import app
from app.services.context import ContextManager
from app.services.copilot import CoPilotService
from app.services.llm import LLMClient


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client that returns a fixed response."""
    client = MagicMock(spec=LLMClient)
    client.generate.return_value = "This is a mocked AI response."
    return client


@pytest.fixture
def context_manager() -> ContextManager:
    """Create a fresh ContextManager for each test."""
    return ContextManager()


@pytest.fixture
def copilot_service(
    mock_llm_client: MagicMock,
    context_manager: ContextManager,
) -> CoPilotService:
    """Create a CoPilotService with mocked dependencies."""
    return CoPilotService(
        llm_client=mock_llm_client,
        context_manager=context_manager,
    )


@pytest.fixture
def client(
    mock_llm_client: MagicMock,
    context_manager: ContextManager,
    copilot_service: CoPilotService,
) -> TestClient:
    """Create a FastAPI TestClient with dependency overrides."""
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    app.dependency_overrides[get_context_manager] = lambda: context_manager
    app.dependency_overrides[get_copilot_service] = lambda: copilot_service

    yield TestClient(app)

    app.dependency_overrides.clear()
