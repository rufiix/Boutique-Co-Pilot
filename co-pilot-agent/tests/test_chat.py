"""Tests for the chat endpoint and CoPilotService."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.services.copilot import CoPilotService


class TestChatEndpoint:
    """Integration tests for the /copilot-api/chat endpoint."""

    def test_basic_chat(self, client: TestClient) -> None:
        """A basic chat message returns a 200 with a response field."""
        payload = {
            "user_id": "test-user",
            "message": "What products do you have?",
        }
        response = client.post("/copilot-api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)

    def test_chat_with_page_context(self, client: TestClient) -> None:
        """Chat with product page context includes the context in the prompt."""
        payload = {
            "user_id": "test-user",
            "message": "What is the price?",
            "page_context": {
                "type": "product_page",
                "name": "Vintage Typewriter",
                "price": "$67.99",
                "description": "A classic mechanical typewriter.",
            },
        }
        response = client.post("/copilot-api/chat", json=payload)
        assert response.status_code == 200

    def test_chat_with_cart(self, client: TestClient) -> None:
        """Chat with cart context processes correctly."""
        payload = {
            "user_id": "test-user",
            "message": "What is in my cart?",
            "cart_contents": {
                "type": "detailed_view",
                "items": [
                    {"name": "Sunglasses", "quantity": 1, "price": "$19.99"},
                ],
                "shipping_cost": "$5.99",
                "total_cost": "$25.98",
            },
        }
        response = client.post("/copilot-api/chat", json=payload)
        assert response.status_code == 200

    def test_chat_with_history(self, client: TestClient) -> None:
        """Chat with conversation history processes correctly."""
        payload = {
            "user_id": "test-user",
            "message": "What did I ask before?",
            "chat_history": [
                "User: Show me sunglasses",
                "Assistant: Here are our sunglasses...",
            ],
        }
        response = client.post("/copilot-api/chat", json=payload)
        assert response.status_code == 200


class TestCoPilotService:
    """Unit tests for the CoPilotService business logic."""

    def test_build_page_context_product(self) -> None:
        """Product page context is formatted correctly."""
        from app.models.schemas import PageContext

        ctx = PageContext(
            type="product_page",
            name="Watch",
            price="$100",
            description="A nice watch.",
        )
        result = CoPilotService._build_page_context(ctx)
        assert "Watch" in result
        assert "$100" in result

    def test_build_page_context_homepage(self) -> None:
        """Homepage context lists products."""
        from app.models.schemas import PageContext

        ctx = PageContext(
            type="homepage",
            products_on_page=[
                {"name": "Hat", "price": "$20"},
                {"name": "Bag", "price": "$40"},
            ],
        )
        result = CoPilotService._build_page_context(ctx)
        assert "Hat" in result
        assert "Bag" in result

    def test_build_page_context_none(self) -> None:
        """None page context returns default message."""
        result = CoPilotService._build_page_context(None)
        assert "not on a specific" in result

    def test_build_cart_context_detailed(self) -> None:
        """Detailed cart view includes item details."""
        from app.models.schemas import Cart, CartItem

        cart = Cart(
            type="detailed_view",
            items=[CartItem(name="Shirt", quantity=2, price="$30")],
            shipping_cost="$5",
            total_cost="$65",
        )
        result = CoPilotService._build_cart_context(cart)
        assert "Shirt" in result
        assert "Quantity: 2" in result

    def test_build_cart_context_summary(self) -> None:
        """Summary cart view shows item count."""
        from app.models.schemas import Cart

        cart = Cart(type="summary_view", item_count=3)
        result = CoPilotService._build_cart_context(cart)
        assert "3 item(s)" in result

    def test_build_history_context_empty(self) -> None:
        """Empty history returns beginning-of-conversation message."""
        result = CoPilotService._build_history_context(None)
        assert "beginning" in result

    def test_process_chat_llm_failure(
        self,
        copilot_service: CoPilotService,
        mock_llm_client: MagicMock,
    ) -> None:
        """LLM failure returns a graceful fallback message."""
        from app.models.schemas import ChatMessage

        mock_llm_client.generate.side_effect = RuntimeError("API down")
        message = ChatMessage(user_id="u1", message="Hello")
        result = copilot_service.process_chat(message)
        assert "trouble" in result
