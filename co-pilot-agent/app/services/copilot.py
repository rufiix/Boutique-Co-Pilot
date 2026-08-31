"""Co-Pilot orchestration service.

Contains the core business logic for assembling multimodal prompts
from user context, page context, cart state, and conversation
history, then delegating to the LLM client for response generation.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.models.schemas import Cart, ChatMessage, PageContext
from app.services.context import ContextManager
from app.services.llm import LLMClient

logger: logging.Logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE: str = """
You are an e-commerce assistant. Analyze the user's question and the provided image (if any).

Context:
* Conversation History: {history_text}
* Shopping Cart: {cart_text}
* Current Page: {page_context_text}
* Recently Viewed Products: {viewed_products}

User's Question: "{user_message}"

Instructions:
1. Analyze all provided context to understand the user's situation.
2. If the user asks to list products on the page and the context indicates the homepage, list products from the products_on_page list.
3. If the user asks about their cart, use the Shopping Cart Context to answer.
4. If the user asks about the current product on a product page (e.g., "what's the price?"), use the Current Page Context.
5. To provide detailed information (materials, sizing, specifications), the user must be on the product detail page. If not, suggest they open the product page first.
6. If the question is about visual aspects of a product (e.g., color, style, pattern), use the IMAGE as the primary source of truth.
7. When describing visual aspects, state them confidently and directly without uncertain language.
8. If the user asks for an opinion or recommendation, be a creative but helpful salesperson.
9. Use the Conversation History to understand flow and answer meta-questions.
10. Prioritize data in this order: Current Page, Shopping Cart, Viewed Products, Conversation History.
11. If context data is missing or unclear, say so and ask for clarification instead of guessing.
12. Keep answers short, warm, and conversational like a boutique shopping assistant.
"""


class CoPilotService:
    """Orchestrates prompt assembly and LLM interaction.

    Composes context from multiple sources (user history, page state,
    cart contents, conversation turns) into a structured prompt,
    delegates to the :class:`LLMClient` for generation, and returns
    the response.

    Attributes:
        _llm_client: The LLM client used for response generation.
        _context_manager: Repository for per-user behavioral context.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        context_manager: ContextManager,
    ) -> None:
        """Initialize the Co-Pilot service.

        Args:
            llm_client: An LLM client implementation.
            context_manager: A user context repository.
        """
        self._llm_client: LLMClient = llm_client
        self._context_manager: ContextManager = context_manager

    def process_chat(self, message: ChatMessage) -> str:
        """Process an inbound chat message and generate an AI response.

        Args:
            message: The chat message containing the user query,
                page context, cart state, and conversation history.

        Returns:
            The AI-generated response string.
        """
        viewed = self._context_manager.get_viewed_products(message.user_id)
        viewed_products: str = ", ".join(viewed) if viewed else "none"

        page_context_text: str = self._build_page_context(message.page_context)
        cart_text: str = self._build_cart_context(message.cart_contents)
        history_text: str = self._build_history_context(message.chat_history)

        prompt: str = SYSTEM_PROMPT_TEMPLATE.format(
            history_text=history_text,
            cart_text=cart_text,
            page_context_text=page_context_text,
            viewed_products=viewed_products,
            user_message=message.message,
        )

        image_url: Optional[str] = None
        if message.page_context and message.page_context.image_url:
            image_url = message.page_context.image_url

        try:
            return self._llm_client.generate(prompt, image_url)
        except RuntimeError:
            return (
                "I'm having a little trouble thinking right now. "
                "Please try again in a moment."
            )

    @staticmethod
    def _build_page_context(page_context: Optional[PageContext]) -> str:
        """Assemble page context text from the PageContext model.

        Args:
            page_context: The current page context, or None.

        Returns:
            A formatted string describing the current page state.
        """
        if not page_context:
            return "User is not on a specific product page."

        if page_context.type == "product_page":
            return (
                f"User is on a product page for:\n"
                f"* Name: {page_context.name}\n"
                f"* Price: {page_context.price}\n"
                f"* Description: {page_context.description}"
            )

        if (
            page_context.type == "homepage"
            and page_context.products_on_page
        ):
            products_list = "\n".join(
                f"* {p['name']} ({p['price']})"
                for p in page_context.products_on_page
            )
            return (
                f"User is on the homepage, which displays these products:\n"
                f"{products_list}"
            )

        return "User is not on a specific product page."

    @staticmethod
    def _build_cart_context(cart: Optional[Cart]) -> str:
        """Assemble cart context text from the Cart model.

        Args:
            cart: The current cart state, or None.

        Returns:
            A formatted string describing the cart contents.
        """
        if not cart:
            return "The user's shopping cart is empty."

        if cart.type == "detailed_view" and cart.items:
            items_text = "\n".join(
                f"* {item.name} (Quantity: {item.quantity}, Price: {item.price})"
                for item in cart.items
            )
            return (
                f"The user is on the cart page. The cart contains:\n"
                f"{items_text}\n"
                f"* Shipping Cost: {cart.shipping_cost}\n"
                f"* Total Cost: {cart.total_cost}"
            )

        if cart.type == "summary_view" and cart.item_count and cart.item_count > 0:
            return f"The user has {cart.item_count} item(s) in their cart."

        return "The user's shopping cart is empty."

    @staticmethod
    def _build_history_context(history: Optional[list[str]]) -> str:
        """Assemble conversation history text.

        Args:
            history: List of previous conversation turns, or None.

        Returns:
            A formatted string of conversation history.
        """
        if not history:
            return "This is the beginning of the conversation."
        return (
            "Here is the recent conversation history:\n"
            + "\n".join(history)
        )
