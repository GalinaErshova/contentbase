"""Пакет ContentBase.

Локальная multi-agent RAG-система для курса OTUS LLM Driven Development.
"""

from contentbase.config import get_settings, Settings
from contentbase.schemas import (
    Document,
    Chunk,
    RetrievedChunk,
    RagAnswer,
    EvaluationResult,
)
from contentbase.ingestion import DocumentLoader
from contentbase.chunking import Chunker
from contentbase.generation import Generator, OllamaClient
from contentbase.summarization import Summarizer
from contentbase.tracing import get_tracing_client, TracingClient


def main():
    """Запустить CLI-приложение ContentBase."""
    from contentbase.app import app

    app()


__all__ = [
    "get_settings",
    "Settings",
    "Document",
    "Chunk",
    "RetrievedChunk",
    "RagAnswer",
    "EvaluationResult",
    "DocumentLoader",
    "Chunker",
    "Generator",
    "OllamaClient",
    "Summarizer",
    "get_tracing_client",
    "TracingClient",
    "main",
]
