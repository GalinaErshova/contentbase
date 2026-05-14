"""Модуль генерации ContentBase с mock-режимом Ollama.

Mock-реализация нужна для тестирования без запущенного сервера Ollama.
"""
from pathlib import Path
from typing import Optional
from datetime import datetime

from contentbase.config import get_settings
from contentbase.evaluation import (
    build_llm_judge_prompt,
    estimate_usage_details,
    evaluate_answer,
    parse_judge_score,
)
from contentbase.schemas import RagAnswer
from contentbase.tracing import get_tracing_client


SUPPORTED_CONTEXT_SUFFIXES = {".md", ".txt"}


def load_context_from_path(context_path: str) -> tuple[str, list[str]]:
    """Загрузить контекст из одного файла или из директории.

    Если передан файл, читается только он. Если передана директория,
    рекурсивно читаются все .md и .txt файлы внутри неё.

    Args:
        context_path: Путь к файлу или директории с документами.

    Returns:
        Кортеж из общего текста контекста и списка файлов-источников.

    Raises:
        FileNotFoundError: Если путь не существует.
        ValueError: Если файл неподдерживаемого типа или в директории нет документов.
    """
    path = Path(context_path)

    if not path.exists():
        raise FileNotFoundError(f"Context path does not exist: {context_path}")

    if path.is_file():
        if path.suffix not in SUPPORTED_CONTEXT_SUFFIXES:
            raise ValueError("Only .md and .txt files are supported as context")
        return path.read_text(encoding="utf-8"), [str(path)]

    files = sorted(
        file_path
        for file_path in path.rglob("*")
        if file_path.is_file() and file_path.suffix in SUPPORTED_CONTEXT_SUFFIXES
    )

    if not files:
        raise ValueError(f"No .md or .txt documents found in directory: {context_path}")

    context_parts = []
    sources = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        sources.append(str(file_path))
        context_parts.append(
            f"--- SOURCE: {file_path} ---\n"
            f"{text.strip()}\n"
        )

    return "\n\n".join(context_parts), sources


class OllamaClientMock:
    """Mock-клиент Ollama API для тестирования без сервера Ollama."""

    def __init__(self):
        self.settings = get_settings()
        self.call_count = 0

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Сгенерировать mock-текст.

        Args:
            prompt: Входной prompt.
            model: Модель для генерации (в mock-режиме игнорируется).
            temperature: Температура sampling (в mock-режиме игнорируется).
            max_tokens: Максимум токенов для генерации (в mock-режиме игнорируется).

        Returns:
            Сгенерированный mock-текст.
        """
        self.call_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Генерируем mock-ответы по ключевым словам в prompt.
        prompt_lower = prompt.lower()

        if "summary" in prompt_lower or "summarize" in prompt_lower:
            return f"[MOCK] Summary generated at {timestamp}: This is a mock summary of the document. The key points would be extracted and condensed into a brief overview focusing on main ideas and essential information."

        elif "question" in prompt_lower:
            if "rag" in prompt_lower or "retrieval" in prompt_lower:
                return f"[MOCK] RAG answer at {timestamp}: Based on the retrieved context, RAG (Retrieval-Augmented Generation) combines information retrieval with text generation. It allows LLMs to access external knowledge bases while maintaining factual accuracy."

            elif "context" in prompt_lower:
                return f"[MOCK] Context-based answer at {timestamp}: According to the provided document/context, the answer would be: [source: document]"

            else:
                return f"[MOCK] Answer at {timestamp}: This is a mock answer to the question. In a real implementation, this would use the actual LLM to generate a context-aware response."

        else:
            return f"[MOCK] Generated at {timestamp}: This is a mock response. The actual implementation would use Ollama API to generate text based on the provided prompt and parameters."

    def get_call_count(self) -> int:
        """Получить количество выполненных mock-вызовов.

        Returns:
            Количество вызовов.
        """
        return self.call_count


# Проверяем, можно ли использовать реальный клиент Ollama.
try:
    import httpx
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaClient:
    """Клиент Ollama API с fallback на mock-режим."""

    def __init__(self):
        self.settings = get_settings()
        self.mock_mode = not OLLAMA_AVAILABLE

        if self.mock_mode:
            print("[MOCK MODE] Using OllamaMock - no real Ollama server needed")
            self.client = OllamaClientMock()
        else:
            self.client = httpx.Client(
                base_url=self.settings.ollama_base_url,
                timeout=self.settings.ollama_timeout_seconds,
            )
            try:
                self.client.get("/api/tags", timeout=2.0).raise_for_status()
                print("[REAL MODE] Using real Ollama client")
            except Exception as exc:
                print(f"[MOCK MODE] Ollama unavailable, using OllamaMock: {exc}")
                self.mock_mode = True
                self.client.close()
                self.client = OllamaClientMock()

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Сгенерировать текст через Ollama или mock-режим.

        Args:
            prompt: Входной prompt.
            model: Модель для генерации (по умолчанию берётся из настроек).
            temperature: Температура sampling.
            max_tokens: Максимум токенов для генерации.

        Returns:
            Сгенерированный текст.
        """
        model = model or self.settings.ollama_chat_model

        if self.mock_mode:
            return self.client.generate(prompt, model, temperature, max_tokens)

        # Вызов реального Ollama API.
        response = self.client.post(
            "/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
        )

        response.raise_for_status()
        result = response.json()
        return result.get("response", "")


class Generator:
    """Генерирует ответы и контент с помощью Ollama."""

    def __init__(self):
        self.client = OllamaClient()

    def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        context_file: Optional[str] = None,
        evaluate: bool = True,
        llm_judge: bool = False,
    ) -> RagAnswer:
        """Ответить на вопрос с необязательным контекстом.

        Args:
            question: Вопрос пользователя.
            context: Текст контекста для Phase 2 RAG.
            context_file: Путь к файлу или директории контекста для Phase 1 basic Q&A.

        Returns:
            RagAnswer с ответом и источниками.
        """
        tracing = get_tracing_client()
        sources = []
        context_text = context

        # Собираем prompt.
        if context:
            # Phase 2: RAG-режим с найденным контекстом.
            sources = ["retrieved_context"]
            prompt = f"""You are a helpful assistant answering questions based on provided context.

Context:
{context}

Question: {question}

Answer: question using ONLY the provided context. If context doesn't contain enough information to answer, say "I don't have enough information in context to answer this question."

Be concise and accurate. Include citations in the format [source: doc_id]."""
        elif context_file:
            # Phase 1: basic Q&A с полным контекстом файла или директории.
            with tracing.span(
                "load_context",
                input_data={"context_file": context_file},
                metadata={"mode": "basic"},
            ):
                context_text, sources = load_context_from_path(context_file)
                tracing.update_current_span(
                    output={
                        "source_count": len(sources),
                        "context_length": len(context_text),
                    },
                    metadata={"sources": sources},
                )
            prompt = f"""You are a helpful assistant answering questions based on provided document.

Document:
{context_text}

Question: {question}

Answer: question using ONLY the provided document. If document doesn't contain enough information to answer, say "I don't have enough information in document to answer this question."

Be concise and accurate. Include citations in the format [source: filename]."""
        else:
            # Без контекста: обычная генерация.
            prompt = f"""You are a helpful assistant.

Question: {question}

Provide a helpful answer."""

        # Генерируем ответ.
        model = self.client.settings.ollama_chat_model
        with tracing.span(
            "build_prompt",
            metadata={
                "has_context": bool(context_text),
                "context_file": context_file,
                "source_count": len(sources),
                "prompt_length": len(prompt),
            },
        ):
            tracing.update_current_span(output={"prompt_preview": prompt[:500]})

        with tracing.generation(
            "llm_generation",
            model=model,
            input_data=prompt,
            model_parameters={"temperature": 0.7, "max_tokens": 1024},
            metadata={
                "mock_mode": self.client.mock_mode,
                "context_length": len(context_text or ""),
                "sources": sources,
            },
        ):
            answer = self.client.generate(prompt, temperature=0.7, max_tokens=1024)
            tracing.update_current_generation(
                output=answer,
                metadata={"answer_length": len(answer)},
                usage_details=estimate_usage_details(prompt, answer),
            )

        if evaluate:
            with tracing.span(
                "custom_evaluator",
                as_type="evaluator",
                input_data={
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                },
                metadata={"evaluator": "contentbase_heuristic_v1"},
            ):
                evaluation = evaluate_answer(
                    question=question,
                    answer=answer,
                    context=context_text,
                    sources=sources,
                )
                evaluation_data = evaluation.model_dump()
                tracing.update_current_span(output=evaluation_data)
                for score_name, score_value in evaluation_data.items():
                    tracing.log_score(
                        score_name,
                        score_value,
                        comment="ContentBase custom heuristic evaluator",
                        metadata={"evaluator": "contentbase_heuristic_v1"},
                    )

        if llm_judge:
            judge_prompt = build_llm_judge_prompt(question, answer, context_text)
            with tracing.generation(
                "llm_as_a_judge",
                model=model,
                input_data=judge_prompt,
                model_parameters={"temperature": 0.0, "max_tokens": 16},
                metadata={"judge": "ollama_numeric_quality_score"},
            ):
                judge_output = self.client.generate(
                    judge_prompt,
                    temperature=0.0,
                    max_tokens=16,
                )
                judge_score = parse_judge_score(judge_output)
                tracing.update_current_generation(
                    output=judge_output,
                    usage_details=estimate_usage_details(judge_prompt, judge_output),
                )
                tracing.log_score(
                    "llm_as_judge_score",
                    judge_score,
                    comment="LLM-as-a-judge numeric score from Ollama",
                    metadata={"judge_model": model},
                )

        return RagAnswer(
            answer=answer,
            sources=sources,
            confidence=0.8,  # Заглушка: в Phase 3 будет рассчитываться отдельно.
        )
