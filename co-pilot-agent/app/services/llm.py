"""LLM client abstraction layer.

Provides a protocol-based interface for generative model interactions,
with a concrete implementation for Google Vertex AI Gemini. The
abstraction enables straightforward mocking in tests and future
provider swaps without touching business logic.
"""

from __future__ import annotations

import abc
import logging
from typing import Any, List, Optional, Protocol

import requests
import vertexai
from vertexai.generative_models import GenerativeModel, Image, Part

from app.config import Settings

logger: logging.Logger = logging.getLogger(__name__)


class LLMClient(abc.ABC):
    """Abstract interface for large language model interactions.

    Implementations must provide a :meth:`generate` method that accepts
    a text prompt and an optional image URL, returning the model's
    text response.
    """

    @abc.abstractmethod
    def generate(
        self,
        prompt: str,
        image_url: Optional[str] = None,
    ) -> str:
        """Generate a text response from the model.

        Args:
            prompt: The text prompt to send to the model.
            image_url: Optional URL of an image for multimodal analysis.

        Returns:
            The model's generated text response.
        """


class VertexAIClient(LLMClient):
    """Concrete LLM client backed by Google Vertex AI Gemini.

    Initializes the Vertex AI SDK and constructs a
    :class:`GenerativeModel` instance on first use.

    Attributes:
        _model: The underlying Vertex AI generative model.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the Vertex AI client.

        Args:
            settings: Application settings containing GCP project,
                region, and model name.
        """
        vertexai.init(
            project=settings.gcp_project,
            location=settings.gcp_region,
        )
        self._model: GenerativeModel = GenerativeModel(settings.model_name)

    def generate(
        self,
        prompt: str,
        image_url: Optional[str] = None,
    ) -> str:
        """Send a prompt (with optional image) to Gemini and return the response.

        Args:
            prompt: Text prompt including all assembled context.
            image_url: Optional product image URL for multimodal input.

        Returns:
            The generated text response from the model.

        Raises:
            RuntimeError: If the model fails to generate a response.
        """
        parts: list[Any] = [prompt]

        if image_url:
            try:
                image_response = requests.get(image_url, timeout=10)
                image_response.raise_for_status()
                image = Image.from_bytes(image_response.content)
                parts.append(image)
            except Exception as exc:
                logger.warning(
                    "Failed to download product image from %s: %s",
                    image_url,
                    exc,
                )

        try:
            response = self._model.generate_content(parts)
            return response.text
        except Exception as exc:
            logger.error("Model generation failed: %s", exc)
            raise RuntimeError(
                "Failed to generate AI response. Please try again."
            ) from exc
