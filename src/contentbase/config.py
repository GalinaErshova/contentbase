"""Загрузка конфигурации ContentBase.

Настройки читаются из переменных окружения через pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
    )

    # Настройки Ollama
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL",
    )
    ollama_chat_model: str = Field(
        default="qwen2.5:14b",
        description="Ollama model for text generation",
    )
    ollama_embedding_model: str = Field(
        default="bge-m3",
        description="Ollama model for embeddings (Phase 2)",
    )
    ollama_timeout_seconds: float = Field(
        default=600.0,
        description="Ollama request timeout in seconds",
    )

    # Настройки Qdrant (Phase 2)
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant API URL (Phase 2)",
    )
    qdrant_collection_name: str = Field(
        default="contentbase",
        description="Qdrant collection name",
    )

    # Настройки Langfuse
    langfuse_public_key: str = Field(
        default="",
        description="Langfuse public key",
    )
    langfuse_secret_key: str = Field(
        default="",
        description="Langfuse secret key",
    )
    langfuse_host: str = Field(
        default="http://localhost:3000",
        description="Langfuse host URL",
    )

    # Настройки приложения
    default_language: str = Field(
        default="ru",
        description="Default language for documents",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )


def get_settings() -> Settings:
    """Получить настройки приложения."""
    return Settings()
