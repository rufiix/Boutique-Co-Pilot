"""Application configuration via Pydantic Settings.

Centralizes all environment-driven configuration for the Co-Pilot
Agent, including GCP project identifiers and model parameters.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Immutable application settings sourced from environment variables.

    Attributes:
        gcp_project: Google Cloud project identifier.
        gcp_region: Vertex AI deployment region.
        model_name: Generative model identifier for Vertex AI.
        allowed_origins: Comma-separated list of CORS allowed origins.
        log_level: Application log level.
    """

    gcp_project: str = ""
    gcp_region: str = "us-central1"
    model_name: str = "gemini-2.0-flash-lite"
    allowed_origins: str = "*"
    log_level: str = "INFO"

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def cors_origins(self) -> list[str]:
        """Parse allowed_origins into a list of origin strings."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


def get_settings() -> Settings:
    """Factory function for Settings, enables dependency injection override.

    Returns:
        A configured Settings instance.
    """
    return Settings()
