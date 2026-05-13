"""Модуль саммаризации ContentBase.

Делает краткие пересказы документов с помощью Ollama.
"""
from pathlib import Path

from contentbase.generation import OllamaClient
from contentbase.schemas import Document


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

        summary = self.client.generate(prompt, temperature=0.5, max_tokens=512)
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
        # Загружаем документ напрямую; в будущем лучше использовать ingestion.
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

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
