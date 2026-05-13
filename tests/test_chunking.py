"""Тесты для модуля чанкинга ContentBase."""

from contentbase.schemas import Document
from contentbase.chunking import Chunker


def test_chunker_initialization():
    """Проверяем, что Chunker инициализируется с нужными параметрами."""
    chunker = Chunker(chunk_size_chars=1000, chunk_overlap_chars=100)
    assert chunker.chunk_size_chars == 1000
    assert chunker.chunk_overlap_chars == 100


def test_chunk_id_generation():
    """Проверяем, что ID чанков стабильные и детерминированные."""
    chunker = Chunker()
    chunk_id = chunker.generate_chunk_id("test_doc_001", 5)
    assert chunk_id == "test_doc_001_chunk_0005"


def test_chunk_id_zero_padding():
    """Проверяем, что ID чанков дополняются нулями."""
    chunker = Chunker()
    chunk_id = chunker.generate_chunk_id("test_doc", 1)
    assert chunk_id == "test_doc_chunk_0001"

    chunk_id = chunker.generate_chunk_id("test_doc", 123)
    assert chunk_id == "test_doc_chunk_0123"


def test_short_document_single_chunk():
    """Проверяем, что короткий документ превращается в один чанк."""
    chunker = Chunker(chunk_size_chars=1200, chunk_overlap_chars=200)

    doc = Document(
        doc_id="short_doc",
        title="Short Document",
        source="test",
        topic="test",
        language="ru",
        created_at="",
        text=("This is a short document. " * 10),  # Около 250 символов.
    )

    chunks = chunker.chunk(doc)

    assert len(chunks) == 1
    assert chunks[0].doc_id == "short_doc"
    assert chunks[0].chunk_index == 0
    assert len(chunks[0].text) <= 1200


def test_long_document_multiple_chunks():
    """Проверяем, что длинный документ разбивается на чанки с перекрытием."""
    chunker = Chunker(chunk_size_chars=500, chunk_overlap_chars=100)

    doc = Document(
        doc_id="long_doc",
        title="Long Document",
        source="test",
        topic="test",
        language="ru",
        created_at="",
        text="A" * 1000,  # 1000 символов.
    )

    chunks = chunker.chunk(doc)

    # Должно получиться несколько чанков.
    assert len(chunks) > 1

    # Проверяем первый чанк.
    assert chunks[0].chunk_index == 0
    assert len(chunks[0].text) <= 500

    # Проверяем второй чанк.
    if len(chunks) > 1:
        assert chunks[1].chunk_index == 1
        # Второй чанк должен пересекаться с первым.
        assert len(chunks[1].text) <= 500

    # Проверяем перекрытие.
    if len(chunks) > 1:
        # Первый чанк заканчивается символами 'A'.
        # Второй чанк должен начинаться с части этих символов из перекрытия.
        overlap_text = chunks[0].text[-100:]
        assert chunks[1].text.startswith(overlap_text)


def test_metadata_preservation():
    """Проверяем, что метаданные документа сохраняются в чанках."""
    chunker = Chunker()

    doc = Document(
        doc_id="meta_doc",
        title="Test Metadata",
        source="external_articles",
        topic="llmops",
        language="ru",
        created_at="2026-05-12",
        text=("Content to chunk. " * 50),  # Около 900 символов.
    )

    chunks = chunker.chunk(doc)

    # У всех чанков должны быть одинаковые метаданные исходного документа.
    for chunk in chunks:
        assert chunk.doc_id == "meta_doc"
        assert chunk.title == "Test Metadata"
        assert chunk.source == "external_articles"
        assert chunk.topic == "llmops"
        assert chunk.chunk_index in range(len(chunks))
        assert chunk.embedding is None  # В Phase 1 embedding ещё не задаётся.


def test_chunk_count_calculations():
    """Проверяем, что количество чанков рассчитывается корректно."""
    chunker = Chunker(chunk_size_chars=300, chunk_overlap_chars=50)

    # Длина текста = 1000.
    # Размер шага = 300 - 50 = 250.
    # Ожидаемые чанки: (1000 - 300) // 250 + 1 = 3 чанка + остаток.
    text = "A" * 1000

    doc = Document(
        doc_id="calc_doc",
        title="Calc Test",
        source="test",
        topic="test",
        language="ru",
        created_at="",
        text=text,
    )

    chunks = chunker.chunk(doc)

    # Должно получиться несколько чанков.
    assert len(chunks) >= 3
    assert len(chunks) <= 4  # Может быть 4, если остаток создаёт маленький последний чанк.


def test_chunk_documents_multiple_docs():
    """Проверяем чанкинг нескольких документов."""
    chunker = Chunker(chunk_size_chars=200, chunk_overlap_chars=50)

    doc1_text = ("Content " * 30)  # Около 180 символов.
    doc2_text = ("More content " * 40)  # Около 240 символов.

    docs = [
        Document(
            doc_id="doc1",
            title="Document 1",
            source="test",
            topic="test",
            language="ru",
            created_at="",
            text=doc1_text,
        ),
        Document(
            doc_id="doc2",
            title="Document 2",
            source="test",
            topic="test",
            language="ru",
            created_at="",
            text=doc2_text,
        ),
    ]

    chunks = chunker.chunk_documents(docs)

    # Проверяем, что для обоих документов получились осмысленные чанки.
    assert len(chunks) >= 2

    # Проверяем, что есть чанки от обоих документов.
    doc1_chunks = [c for c in chunks if c.doc_id == "doc1"]
    doc2_chunks = [c for c in chunks if c.doc_id == "doc2"]

    assert len(doc1_chunks) > 0
    assert len(doc2_chunks) > 0
