"""Модуль загрузки документов ContentBase.

Загружает документы с диска и извлекает метаданные.
"""
from pathlib import Path
from typing import List, Optional
import re
from langdetect import detect  # type: ignore[import-untyped]

from contentbase.schemas import Document
from contentbase.config import get_settings


def slugify(text: str) -> str:
    """Преобразовать текст в slug, удобный для ID и URL.

    Args:
        text: Исходный текст.

    Returns:
        Текст в формате slug.
    """
    # Переводим в нижний регистр и заменяем пробелы на подчёркивания.
    slug = text.lower().replace(" ", "_")
    # Удаляем спецсимволы, кроме латинских букв, цифр и подчёркивания.
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    # Схлопываем несколько подчёркиваний подряд в одно.
    slug = re.sub(r"_+", "_", slug)
    # Убираем подчёркивания в начале и конце.
    slug = slug.strip("_")
    return slug


def generate_doc_id(filename: str) -> str:
    """Сгенерировать стабильный ID документа из имени файла.

    Args:
        filename: Имя исходного файла.

    Returns:
        Стабильный ID документа.
    """
    name_without_ext = Path(filename).stem
    return slugify(name_without_ext)


def extract_title_from_md(text: str, filename: str) -> str:
    """Извлечь заголовок из Markdown-документа.

    Сначала ищет H1-заголовок (# Title), иначе использует имя файла.

    Args:
        text: Текст документа.
        filename: Имя исходного файла.

    Returns:
        Заголовок документа.
    """
    # Ищем первый H1-заголовок.
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # Если заголовка нет, используем имя файла.
    return Path(filename).stem.replace("_", " ").title()


def extract_topic_from_path(file_path: Path) -> str:
    """Извлечь тему из структуры директорий.

    E.g., data/raw/llmops/file.md -> topic="llmops"
    E.g., data/raw/file.md -> topic="course_notes"

    Args:
        file_path: Путь к документу.

    Returns:
        Строка с темой документа.
    """
    parent = file_path.parent
    if parent.name == "raw":
        # Прямой родитель "raw" считается темой.
        if parent.parent.name != "data":
            return slugify(parent.name)
    return "course_notes"


def extract_source_from_path(file_path: Path) -> str:
    """Извлечь источник из структуры директорий.

    E.g., data/raw/llmops/file.md -> source="course_notes"
    E.g., data/raw/external_articles/file.md -> source="external_articles"

    Args:
        file_path: Путь к документу.

    Returns:
        Строка с источником документа.
    """
    parent = file_path.parent
    if parent.name == "raw":
        # Проверяем, есть ли отдельная директория темы/источника.
        if parent.parent.name == "data":
            topic_dir = parent
            if topic_dir.name != "raw":
                # data/raw/<source>/file.md
                return slugify(topic_dir.name)
    return "course_notes"


def detect_language(text: str, default: str = "ru") -> str:
    """Определить язык текста.

    Args:
        text: Текст для анализа.
        default: Язык по умолчанию, если определение не удалось.

    Returns:
        Код языка, например "ru" или "en".
    """
    try:
        lang = detect(text)
        return lang if lang else default
    except Exception:
        return default


class DocumentLoader:
    """Загружает документы из директории data/raw/."""

    def __init__(self):
        self.settings = get_settings()

    def load_file(self, file_path: Path) -> Optional[Document]:
        """Загрузить один файл документа.

        Args:
            file_path: Путь к файлу документа.

        Returns:
            Объект Document или None, если тип файла не поддерживается.
        """
        # Поддерживаем только .md и .txt файлы.
        if file_path.suffix not in [".md", ".txt"]:
            return None

        # Читаем содержимое файла.
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

        # Пропускаем пустые файлы.
        if not text.strip():
            return None

        # Извлекаем метаданные.
        doc_id = generate_doc_id(file_path.name)
        title = extract_title_from_md(text, file_path.name)
        topic = extract_topic_from_path(file_path)
        source = extract_source_from_path(file_path)
        language = detect_language(text, self.settings.default_language)

        return Document(
            doc_id=doc_id,
            title=title,
            source=source,
            topic=topic,
            language=language,
            created_at="",  # Позже можно заполнить из метаданных файла.
            text=text,
        )

    def load_dir(self, directory: str) -> List[Document]:
        """Загрузить все документы из директории.

        Args:
            directory: Путь к директории, например "data/raw".

        Returns:
            Список объектов Document.
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Directory {directory} does not exist")
            return []

        documents = []
        for file_path in dir_path.rglob("*.md"):
            doc = self.load_file(file_path)
            if doc:
                documents.append(doc)

        for file_path in dir_path.rglob("*.txt"):
            doc = self.load_file(file_path)
            if doc:
                documents.append(doc)

        print(f"Loaded {len(documents)} documents from {directory}")
        return documents
