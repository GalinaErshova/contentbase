"""Кастомная оценка качества ответов ContentBase."""
from __future__ import annotations

import re
from typing import Iterable

from contentbase.schemas import EvaluationResult


TOKEN_RE = re.compile(r"[a-zа-яё0-9]{3,}", re.IGNORECASE)
UNKNOWN_MARKERS = (
    "don't have enough information",
    "not enough information",
    "недостаточно информации",
    "не хватает информации",
    "не знаю",
)


def evaluate_answer(
    *,
    question: str,
    answer: str,
    context: str | None,
    sources: Iterable[str],
) -> EvaluationResult:
    """Оценить ответ простыми воспроизводимыми метриками.

    Это custom evaluator для демонстрации Langfuse scores. Он не заменяет
    экспертную оценку, но дает стабильные числовые метрики для traces.
    """
    answer_relevance = _overlap_score(question, answer)
    context_usage = _context_usage_score(answer, context)
    citation_presence = _citation_score(answer, sources)
    honesty_when_unknown = _honesty_score(answer, context)

    final_score = (
        0.4 * answer_relevance
        + 0.3 * context_usage
        + 0.2 * citation_presence
        + 0.1 * honesty_when_unknown
    )

    return EvaluationResult(
        answer_relevance=round(answer_relevance, 3),
        context_usage=round(context_usage, 3),
        citation_presence=round(citation_presence, 3),
        honesty_when_unknown=round(honesty_when_unknown, 3),
        final_score=round(final_score, 3),
    )


def build_llm_judge_prompt(question: str, answer: str, context: str | None) -> str:
    """Собрать prompt для LLM-as-a-judge."""
    context_block = context or "Контекст не был передан."
    return f"""Оцени качество ответа на вопрос по шкале от 0 до 1.

Верни только число от 0 до 1, без пояснений.

Критерии:
- ответ отвечает на вопрос;
- ответ опирается на контекст, если он есть;
- ответ не выдумывает факты;
- если данных нет, ответ честно сообщает об этом.

Вопрос:
{question}

Контекст:
{context_block[:6000]}

Ответ:
{answer}

Оценка:"""


def parse_judge_score(text: str) -> float:
    """Извлечь числовую оценку из ответа LLM-судьи."""
    match = re.search(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", text.replace(",", "."))
    if not match:
        return 0.0
    return max(0.0, min(1.0, float(match.group(0))))


def estimate_usage_details(prompt: str, output: str) -> dict[str, int]:
    """Грубая оценка токенов для Langfuse, если провайдер не вернул usage."""
    prompt_tokens = max(1, len(prompt) // 4)
    completion_tokens = max(1, len(output) // 4)
    return {
        "input": prompt_tokens,
        "output": completion_tokens,
        "total": prompt_tokens + completion_tokens,
    }


def _token_set(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def _overlap_score(left: str, right: str) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)
    if not left_tokens:
        return 0.0
    return min(1.0, len(left_tokens & right_tokens) / len(left_tokens))


def _context_usage_score(answer: str, context: str | None) -> float:
    if not context:
        return 1.0
    answer_tokens = _token_set(answer)
    context_tokens = _token_set(context)
    if not answer_tokens:
        return 0.0
    return min(1.0, len(answer_tokens & context_tokens) / max(1, len(answer_tokens)))


def _citation_score(answer: str, sources: Iterable[str]) -> float:
    if not list(sources):
        return 1.0
    return 1.0 if "[source:" in answer.lower() else 0.0


def _honesty_score(answer: str, context: str | None) -> float:
    if context and context.strip():
        return 1.0
    answer_lower = answer.lower()
    return 1.0 if any(marker in answer_lower for marker in UNKNOWN_MARKERS) else 0.5
