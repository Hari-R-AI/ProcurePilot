"""Configuration management for ProcurePilot using Pydantic Settings.

This module provides environment-based configuration with type safety.
All secrets (API keys, database URLs) should be provided via environment variables.
See .env.example for the template.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Environment variables are automatically mapped to these fields.
    Example:
        PROCUREPILOT_APP_NAME=MyApp
        PROCUREPILOT_DEBUG=True
        PROCUREPILOT_GROQ_API_KEY=xxx
    """

    # Application
    app_name: str = "ProcurePilot"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_headers: list[str] = ["*"]
    
    # Database - SQLite for local dev, PostgreSQL for production
    # TODO: Add DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD for PostgreSQL
    database_url: str = "sqlite:///./procurepilot.db"
    
    # LLM / Groq
    # TODO: Set GROQ_API_KEY environment variable before running
    # Generate at: https://console.groq.com/
    groq_api_key: str = ""  # Leave empty, set via env
    groq_model: str = "mixtral-8x7b-32768"  # Can be overridden via env
    
    # ChromaDB
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "procurement_policies"
    
    # Feature flags
    enable_auth: bool = False  # TODO: Implement authentication
    enable_audit_log: bool = True
    enable_policy_retrieval: bool = True
    
    # Request tracking
    enable_request_tracing: bool = True
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_prefix = "PROCUREPILOT_"
        case_sensitive = False
        extra = "allow"  # Allow extra env vars


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
