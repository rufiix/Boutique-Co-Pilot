"""User context management service.

Provides a repository for tracking per-user behavioral signals
(e.g., viewed products) that feed into the prompt engineering
pipeline for context-aware AI responses.
"""

from __future__ import annotations

import logging
from typing import Dict, List

logger: logging.Logger = logging.getLogger(__name__)


class ContextManager:
    """In-memory repository for per-user browsing context.

    Stores a mapping of user IDs to their accumulated behavioral
    signals.  In a production environment, this should be backed by
    an external store such as Redis or Memorystore.

    Attributes:
        _store: Internal dictionary mapping user IDs to context dicts.
    """

    def __init__(self) -> None:
        """Initialize an empty context store."""
        self._store: Dict[str, Dict[str, List[str]]] = {}

    def record_product_view(self, user_id: str, product_id: str) -> None:
        """Record that a user viewed a specific product.

        Deduplicates product IDs per user.

        Args:
            user_id: The unique session identifier of the user.
            product_id: The identifier of the viewed product.
        """
        if user_id not in self._store:
            self._store[user_id] = {"viewed_products": []}
        if product_id not in self._store[user_id]["viewed_products"]:
            self._store[user_id]["viewed_products"].append(product_id)
            logger.debug(
                "Recorded product view: user=%s, product=%s",
                user_id,
                product_id,
            )

    def get_viewed_products(self, user_id: str) -> List[str]:
        """Retrieve the list of products viewed by a user.

        Args:
            user_id: The unique session identifier of the user.

        Returns:
            A list of product IDs the user has viewed, or an empty
            list if no views have been recorded.
        """
        context = self._store.get(user_id, {"viewed_products": []})
        return context["viewed_products"]

    def clear_user(self, user_id: str) -> None:
        """Remove all stored context for a user.

        Args:
            user_id: The unique session identifier of the user.
        """
        self._store.pop(user_id, None)
