"""Chat endpoint for the Co-Pilot assistant."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_copilot_service
from app.models.schemas import ChatMessage, ChatResponse
from app.services.copilot import CoPilotService

router: APIRouter = APIRouter(prefix="/copilot-api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_copilot(
    chat_message: ChatMessage,
    copilot: CoPilotService = Depends(get_copilot_service),
) -> ChatResponse:
    """Process a user chat message and return an AI-generated response.

    Delegates to the :class:`CoPilotService` for context assembly,
    prompt engineering, and LLM interaction.

    Args:
        chat_message: The inbound chat message with full context.
        copilot: Injected Co-Pilot service instance.

    Returns:
        A ChatResponse containing the assistant's reply.
    """
    response_text: str = copilot.process_chat(chat_message)
    return ChatResponse(response=response_text)
