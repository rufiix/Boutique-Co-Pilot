"""Tests for the event ingestion endpoint and ContextManager."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.services.context import ContextManager


class TestEventEndpoint:
    """Integration tests for the /copilot-api/event endpoint."""

    def test_receive_event(self, client: TestClient) -> None:
        """A valid event returns 200 with acknowledgement."""
        payload = {
            "user_id": "test-user",
            "event_type": "product_view",
            "product_id": "OLJCESPC7Z",
        }
        response = client.post("/copilot-api/event", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "event received"

    def test_receive_event_missing_fields(self, client: TestClient) -> None:
        """An event missing required fields returns 422."""
        response = client.post(
            "/copilot-api/event",
            json={"user_id": "test-user"},
        )
        assert response.status_code == 422


class TestContextManager:
    """Unit tests for the ContextManager service."""

    def test_record_and_retrieve(self, context_manager: ContextManager) -> None:
        """Recorded product views are retrievable."""
        context_manager.record_product_view("u1", "prod-a")
        context_manager.record_product_view("u1", "prod-b")
        viewed = context_manager.get_viewed_products("u1")
        assert viewed == ["prod-a", "prod-b"]

    def test_deduplication(self, context_manager: ContextManager) -> None:
        """Duplicate product views are not recorded twice."""
        context_manager.record_product_view("u1", "prod-a")
        context_manager.record_product_view("u1", "prod-a")
        assert context_manager.get_viewed_products("u1") == ["prod-a"]

    def test_unknown_user(self, context_manager: ContextManager) -> None:
        """Unknown user returns an empty list."""
        assert context_manager.get_viewed_products("unknown") == []

    def test_clear_user(self, context_manager: ContextManager) -> None:
        """Clearing a user removes all their context."""
        context_manager.record_product_view("u1", "prod-a")
        context_manager.clear_user("u1")
        assert context_manager.get_viewed_products("u1") == []

    def test_isolation_between_users(
        self, context_manager: ContextManager
    ) -> None:
        """Product views are isolated between users."""
        context_manager.record_product_view("u1", "prod-a")
        context_manager.record_product_view("u2", "prod-b")
        assert context_manager.get_viewed_products("u1") == ["prod-a"]
        assert context_manager.get_viewed_products("u2") == ["prod-b"]


class TestHealthEndpoint:
    """Integration tests for the root health check."""

    def test_health(self, client: TestClient) -> None:
        """Health endpoint returns 200 with status."""
        response = client.get("/")
        assert response.status_code == 200
        assert "status" in response.json()
