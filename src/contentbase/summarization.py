"""Модуль саммаризации ContentBase.

Делает краткие пересказы документов с помощью Ollama.
"""
from pathlib import Path

from contentbase.evaluation import estimate_usage_details
from contentbase.generation import OllamaClient
from contentbase.schemas import Document
from contentbase.tracing import get_tracing_client


class Summarizer:
    """Делает краткие пересказы документов с помощью Ollama."""

    def __init__(self):
        self.client = OllamaClient()

    def summarize_text(self, text: str, max_length: int = 300) -> str:
        """Сделать краткий пересказ текста.

        Args:
            text: Текст для пересказа.
            max_length: Максимальная длина summary в символах.

        Returns:
            Текст краткого пересказа.
        """
        prompt = f"""Summarize the following text in a concise manner.

Text:
{text}

Guidelines:
- Focus on key points and main ideas
- Keep it under {max_length} characters
- Use the same language as the source text
- Maintain accuracy - don't hallucinate information

Summary:"""

        tracing = get_tracing_client()
        model = self.client.settings.ollama_chat_model
        with tracing.generation(
            "summary_generation",
            model=model,
            input_data=prompt,
            model_parameters={"temperature": 0.5, "max_tokens": 512},
            metadata={
                "input_length": len(text),
                "max_summary_length": max_length,
                "mock_mode": self.client.mock_mode,
            },
        ):
            summary = self.client.generate(prompt, temperature=0.5, max_tokens=512)
            tracing.update_current_generation(
                output=summary,
                metadata={"output_length": len(summary)},
                usage_details=estimate_usage_details(prompt, summary),
            )
        return summary

    def summarize_document(self, document: Document) -> dict:
        """Сделать краткий пересказ документа.

        Args:
            document: Документ для пересказа.

        Returns:
            Словарь с summary и метаданными.
        """
        print(f"Summarizing document: {document.doc_id}")

        summary = self.summarize_text(document.text)

        # Рассчитываем коэффициент сжатия текста.
        compression_ratio = len(summary) / len(document.text) if document.text else 0

        return {
            "doc_id": document.doc_id,
            "title": document.title,
            "summary": summary,
            "input_length": len(document.text),
            "output_length": len(summary),
            "compression_ratio": compression_ratio,
        }

    def summarize_file(self, file_path: str) -> dict:
        """Сделать краткий пересказ файла документа.

        Args:
            file_path: Путь к файлу документа.

        Returns:
            Словарь с summary и метаданными.
        """
        tracing = get_tracing_client()

        with tracing.span(
            "load_summary_document",
            input_data={"file_path": file_path},
        ):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            tracing.update_current_span(
                output={"input_length": len(text)},
                metadata={"file_path": file_path},
            )

        # Создаём временный объект Document.
        doc_path = Path(file_path)
        doc = Document(
            doc_id=doc_path.stem,
            title=doc_path.stem,
            source="file",
            topic="unknown",
            language="unknown",
            created_at="",
            text=text,
        )

        return self.summarize_document(doc)
