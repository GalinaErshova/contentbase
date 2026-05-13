"""Модели данных и схемы ContentBase.

Здесь описаны Pydantic-модели для документов, чанков и результатов оценки.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class Document(BaseModel):
    """Модель документа с метаданными."""

    doc_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Document source (e.g., course_notes)")
    topic: str = Field(..., description="Document topic")
    language: str = Field(..., description="Document language code")
    created_at: str = Field(default="", description="Creation timestamp")
    text: str = Field(..., description="Document text content")

    model_config = ConfigDict(
        json_schema_extra={"example": {
            "doc_id": "llmops_intro_001",
            "title": "Введение в LLMOps",
            "source": "course_notes",
            "topic": "llmops",
            "language": "ru",
            "created_at": "2026-05-12",
            "text": "LLMOps is..."
        }}
    )


class Chunk(BaseModel):
    """Модель чанка с метаданными."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Parent document ID")
    title: str = Field(..., description="Document title")
    topic: str = Field(..., description="Document topic")
    chunk_index: int = Field(..., description="Chunk index within document")
    source: str = Field(..., description="Document source")
    text: str = Field(..., description="Chunk text content")
    embedding: Optional[List[float]] = Field(default=None, description="Embedding vector (Phase 2)")

    model_config = ConfigDict(
        json_schema_extra={"example": {
            "chunk_id": "llmops_intro_001_chunk_0001",
            "doc_id": "llmops_intro_001",
            "title": "Введение в LLMOps",
            "topic": "llmops",
            "chunk_index": 1,
            "source": "course_notes",
            "text": "LLMOps is the practice...",
            "embedding": None
        }}
    )


class RetrievedChunk(BaseModel):
    """Чанк, найденный через векторный поиск (Phase 2)."""

    chunk_id: str = Field(..., description="Chunk identifier")
    doc_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    text: str = Field(..., description="Chunk text")
    score: float = Field(..., description="Similarity score")


class RagAnswer(BaseModel):
    """Ответ, сгенерированный RAG-пайплайном."""

    answer: str = Field(..., description="Generated answer")
    sources: List[str] = Field(default_factory=list, description="Source references")
    confidence: float = Field(default=0.0, description="Answer confidence score")


class EvaluationResult(BaseModel):
    """Результат оценки с числовыми метриками."""

    answer_relevance: float = Field(..., description="Answer relevance score (0-1)")
    context_usage: float = Field(..., description="Context usage score (0-1)")
    citation_presence: float = Field(..., description="Citation presence score (0-1)")
    honesty_when_unknown: float = Field(..., description="Honesty score when unknown (0-1)")
    final_score: float = Field(..., description="Final weighted score (0-1)")

    model_config = ConfigDict(
        json_schema_extra={"example": {
            "answer_relevance": 0.8,
            "context_usage": 0.9,
            "citation_presence": 1.0,
            "honesty_when_unknown": 1.0,
            "final_score": 0.88
        }}
    )
