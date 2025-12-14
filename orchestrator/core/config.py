"""
SystemCrafter AI - Orchestrator Core Configuration
"""
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )
    
    # Application
    app_name: str = "SystemCrafter AI"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/systemcrafter"
    )
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # Security
    secret_key: str = Field(default="change-me-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # LLM Provider Selection
    llm_provider: Literal["groq", "ollama"] = "ollama"

    # Ollama (local) Configuration
    ollama_base_url: str = Field(default="http://localhost:11434")

    # LLM Model Settings (default to a local Kimi-K2 model)
    llm_model: str = "kimi-k2:1t-cloud"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 2048

    # Runtime tuning: concurrency and retries
    llm_concurrent_requests: int = 3
    llm_retry_attempts: int = 5
    llm_retry_backoff_seconds: float = 5.0
    
    # GitHub Integration
    github_token: Optional[str] = None
    github_org: Optional[str] = None
    
    # Vector Database
    chroma_persist_directory: str = "./data/chroma"
    
    # Project Output
    projects_dir: str = "./projects"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS
    frontend_url: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
