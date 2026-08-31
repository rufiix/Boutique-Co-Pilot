"""FastAPI application factory.

Constructs the ASGI application with middleware, routers, and
structured logging configuration.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, Settings
from app.routers import chat, events, health


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance.

    Attaches CORS middleware, registers route modules, and configures
    structured logging based on application settings.

    Returns:
        A fully configured :class:`FastAPI` application.
    """
    settings: Settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    app = FastAPI(
        title="Boutique Co-Pilot Agent",
        description=(
            "A proactive, multimodal AI shopping assistant for e-commerce, "
            "powered by Vertex AI Gemini."
        ),
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(events.router)
    app.include_router(chat.router)

    return app


app: FastAPI = create_app()
