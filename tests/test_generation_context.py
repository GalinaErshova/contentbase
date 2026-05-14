"""Тесты для загрузки контекста из файлов и директорий."""

import pytest

from contentbase.generation import load_context_from_path


def test_load_context_from_single_file(tmp_path):
    """Проверяем загрузку контекста из одного файла."""
    context_file = tmp_path / "notes.md"
    context_file.write_text("# Notes\n\nText from one file.", encoding="utf-8")

    context, sources = load_context_from_path(str(context_file))

    assert "Text from one file." in context
    assert sources == [str(context_file)]


def test_load_context_from_directory(tmp_path):
    """Проверяем загрузку всех .md и .txt файлов из директории."""
    context_dir = tmp_path / "context_docs"
    context_dir.mkdir()
    first_file = context_dir / "a.md"
    second_file = context_dir / "b.txt"
    ignored_file = context_dir / "c.pdf"

    first_file.write_text("First document.", encoding="utf-8")
    second_file.write_text("Second document.", encoding="utf-8")
    ignored_file.write_text("Ignored document.", encoding="utf-8")

    context, sources = load_context_from_path(str(context_dir))

    assert "First document." in context
    assert "Second document." in context
    assert "Ignored document." not in context
    assert sources == [str(first_file), str(second_file)]


def test_load_context_from_empty_directory_fails(tmp_path):
    """Проверяем ошибку, если в директории нет поддерживаемых документов."""
    with pytest.raises(ValueError, match="No .md or .txt documents"):
        load_context_from_path(str(tmp_path))
