"""User behavioral event ingestion endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_context_manager
from app.models.schemas import EventResponse, UserEvent
from app.services.context import ContextManager

router: APIRouter = APIRouter(prefix="/copilot-api", tags=["events"])


@router.post("/event", response_model=EventResponse)
def receive_event(
    event: UserEvent,
    context_manager: ContextManager = Depends(get_context_manager),
) -> EventResponse:
    """Ingest a user behavioral event (e.g., product view).

    Records the product view in the per-user context store for
    downstream prompt enrichment.

    Args:
        event: The user event payload.
        context_manager: Injected context manager instance.

    Returns:
        An acknowledgement response.
    """
    context_manager.record_product_view(event.user_id, event.product_id)
    return EventResponse()
