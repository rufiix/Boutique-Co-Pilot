"""Request and response schemas for the Co-Pilot API.

All data transfer objects consumed or emitted by the API endpoints
are defined here using Pydantic models with strict type annotations.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PageContext(BaseModel):
    """Contextual information about the page the user is currently viewing.

    Attributes:
        type: Page category identifier (e.g., ``product_page``, ``homepage``).
        name: Product name, if on a product detail page.
        price: Product price string, if on a product detail page.
        description: Product description text.
        image_url: URL of the product image for multimodal analysis.
        products_on_page: List of product summaries visible on the page.
    """

    type: str
    name: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    products_on_page: Optional[List[dict]] = None


class CartItem(BaseModel):
    """A single item within the shopping cart.

    Attributes:
        name: Display name of the product.
        quantity: Number of units in the cart.
        price: Formatted price string.
    """

    name: str
    quantity: int
    price: str


class Cart(BaseModel):
    """Shopping cart state representation.

    Attributes:
        type: View type (``detailed_view`` or ``summary_view``).
        items: List of cart items (populated in detailed view).
        shipping_cost: Formatted shipping cost string.
        total_cost: Formatted total cost string.
        item_count: Total number of items (used in summary view).
    """

    type: str
    items: Optional[List[CartItem]] = None
    shipping_cost: Optional[str] = None
    total_cost: Optional[str] = None
    item_count: Optional[int] = None


class UserEvent(BaseModel):
    """Behavioral event emitted by the frontend.

    Attributes:
        user_id: Unique user session identifier.
        event_type: Event category (e.g., ``product_view``).
        product_id: Identifier of the product involved in the event.
    """

    user_id: str
    event_type: str
    product_id: str


class ChatMessage(BaseModel):
    """Inbound chat message from the user.

    Attributes:
        user_id: Unique user session identifier.
        message: The user's natural language query.
        page_context: Current page context, if available.
        cart_contents: Current cart state, if available.
        chat_history: Recent conversation turns for multi-turn context.
    """

    user_id: str
    message: str
    page_context: Optional[PageContext] = None
    cart_contents: Optional[Cart] = None
    chat_history: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """Outbound chat response returned to the frontend.

    Attributes:
        response: The AI-generated assistant reply.
    """

    response: str


class EventResponse(BaseModel):
    """Acknowledgement response for received events.

    Attributes:
        status: Status message confirming receipt.
    """

    status: str = "event received"


class HealthResponse(BaseModel):
    """Health check response.

    Attributes:
        status: Service health status string.
    """

    status: str = "Co-Pilot Agent is running"
