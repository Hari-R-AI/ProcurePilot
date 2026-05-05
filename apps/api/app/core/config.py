"""Configuration management for ProcurePilot using Pydantic Settings.

This module provides environment-based configuration with type safety.
All secrets (API keys, database URLs) should be provided via environment variables.
See .env.example for the template.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables are automatically mapped to these fields
    using the prefix PROCUREPILOT_.

    Example:
        PROCUREPILOT_APP_NAME=MyApp
        PROCUREPILOT_DEBUG=True
        PROCUREPILOT_GROQ_API_KEY=gsk_xxx
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PROCUREPILOT_",
        case_sensitive=False,
        extra="allow",  # Allow extra env vars without error
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_name: str = "ProcurePilot"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"

    # -------------------------------------------------------------------------
    # Server
    # -------------------------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    cors_origins: str | list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @property
    def parsed_cors_origins(self) -> list[str]:
        if isinstance(self.cors_origins, str):
            if self.cors_origins.strip().startswith("["):
                import json
                try:
                    return json.loads(self.cors_origins)
                except json.JSONDecodeError:
                    pass
            return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
        return self.cors_origins
    cors_credentials: bool = True
    cors_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    cors_headers: list[str] = ["*"]

    # -------------------------------------------------------------------------
    # Database
    # SQLite for local dev — override DATABASE_URL for PostgreSQL in production
    # Example: PROCUREPILOT_DATABASE_URL=postgresql+asyncpg://user:pass@host/db
    # -------------------------------------------------------------------------
    database_url: str = "sqlite:///./procurepilot.db"

    # -------------------------------------------------------------------------
    # LLM / Groq
    # Generate key at: https://console.groq.com/
    # Set: PROCUREPILOT_GROQ_API_KEY=gsk_xxx
    # -------------------------------------------------------------------------
    groq_api_key: str = ""  # Required — must be set via env
    groq_model: str = "llama-3.1-8b-instant"  # Fast, capable model

    # -------------------------------------------------------------------------
    # ChromaDB (Vector Store)
    # -------------------------------------------------------------------------
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "procurement_policies"

    # -------------------------------------------------------------------------
    # Indian Procurement — Currency & Compliance
    # -------------------------------------------------------------------------
    default_currency: str = "INR"  # ISO 4217 currency code
    # Approval thresholds (INR) — used for routing to L1/L2/L3 approvals
    approval_threshold_l1: float = 100_000.0      # < 1 lakh → L1 (dept head)
    approval_threshold_l2: float = 1_000_000.0   # 1–10 lakh → L2 (procurement committee)
    # > 10 lakh → L3 (management approval)

    # -------------------------------------------------------------------------
    # Feature Flags
    # -------------------------------------------------------------------------
    enable_auth: bool = False
    enable_audit_log: bool = True
    enable_policy_retrieval: bool = True
    enable_request_tracing: bool = True
    enable_telemetry: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application configuration from environment.

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        ProcurePilot
    """
    return Settings()
