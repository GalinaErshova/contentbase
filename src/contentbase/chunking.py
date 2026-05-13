"""Модуль чанкинга ContentBase.

Разбивает документы на чанки с перекрытием.
"""
from typing import List

from contentbase.schemas import Document, Chunk


class Chunker:
    """Разбивает документы на чанки с перекрытием."""

    def __init__(self, chunk_size_chars: int = 1200, chunk_overlap_chars: int = 200):
        """Инициализировать чанкер.

        Args:
            chunk_size_chars: Размер каждого чанка в символах.
            chunk_overlap_chars: Перекрытие между соседними чанками в символах.
        """
        self.chunk_size_chars = chunk_size_chars
        self.chunk_overlap_chars = chunk_overlap_chars

    def generate_chunk_id(self, doc_id: str, chunk_index: int) -> str:
        """Сгенерировать стабильный ID чанка.

        Args:
            doc_id: ID исходного документа.
            chunk_index: Номер чанка внутри документа.

        Returns:
            Стабильный ID чанка.
        """
        # Формат: doc_id_chunk_0001
        chunk_num_str = f"{chunk_index:04d}"
        return f"{doc_id}_chunk_{chunk_num_str}"

    def chunk(self, document: Document) -> List[Chunk]:
        """Разбить один документ на чанки с перекрытием.

        Args:
            document: Документ, который нужно разбить.

        Returns:
            Список объектов Chunk.
        """
        text = document.text
        chunks = []

        # Если текст короче размера чанка, возвращаем один чанк.
        if len(text) <= self.chunk_size_chars:
            chunk = Chunk(
                chunk_id=self.generate_chunk_id(document.doc_id, 0),
                doc_id=document.doc_id,
                title=document.title,
                topic=document.topic,
                chunk_index=0,
                source=document.source,
                text=text,
                embedding=None,
            )
            chunks.append(chunk)
            print(f"Document {document.doc_id}: 1 chunk (text shorter than chunk size)")
            return chunks

        # Рассчитываем параметры чанкинга.
        chunk_size = self.chunk_size_chars
        overlap = self.chunk_overlap_chars
        step_size = chunk_size - overlap

        # Проходим по тексту с заданным шагом.
        start = 0
        chunk_index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            chunk = Chunk(
                chunk_id=self.generate_chunk_id(document.doc_id, chunk_index),
                doc_id=document.doc_id,
                title=document.title,
                topic=document.topic,
                chunk_index=chunk_index,
                source=document.source,
                text=chunk_text,
                embedding=None,
            )
            chunks.append(chunk)

            # Переходим к следующему чанку.
            start += step_size
            chunk_index += 1

        print(f"Document {document.doc_id}: {len(chunks)} chunks")
        return chunks

    def chunk_documents(self, documents: List[Document]) -> List[Chunk]:
        """Разбить несколько документов на чанки.

        Args:
            documents: Список объектов Document.

        Returns:
            Список объектов Chunk для всех документов.
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk(doc)
            all_chunks.extend(chunks)

        print(f"Total chunks from {len(documents)} documents: {len(all_chunks)}")
        return all_chunks
