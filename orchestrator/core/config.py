"""
SystemCrafter AI - Orchestrator Core Configuration
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
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
    
    # OpenAI / LLM
    openai_api_key: str = Field(default="")
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 4096
    
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
    
    # CORS
    frontend_url: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
