"""Модуль трассировки ContentBase через Langfuse.

Записывает traces, spans, generations, events и scores в Langfuse.
"""
from typing import Optional, Dict, Any

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("Warning: Langfuse not installed. Tracing disabled.")

from contentbase.config import get_settings


class TracingClient:
    """Клиент трассировки Langfuse."""

    def __init__(self):
        self.settings = get_settings()
        self.client = None

        if LANGFUSE_AVAILABLE and self.settings.langfuse_public_key:
            try:
                self.client = Langfuse(
                    public_key=self.settings.langfuse_public_key,
                    secret_key=self.settings.langfuse_secret_key,
                    host=self.settings.langfuse_host,
                )
                print("Langfuse tracing initialized")
            except Exception as e:
                print(f"Failed to initialize Langfuse: {e}")
                self.client = None
        else:
            print("Langfuse not configured or not available")

    def is_enabled(self) -> bool:
        """Проверить, включена ли трассировка Langfuse.

        Returns:
            True, если Langfuse настроен и доступен.
        """
        return self.client is not None

    def create_trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Создать новый trace.

        Args:
            name: Имя trace.
            user_id: Идентификатор пользователя.
            session_id: Идентификатор сессии.
            metadata: Метаданные trace.

        Returns:
            Объект trace или None, если трассировка отключена.
        """
        if not self.is_enabled():
            return None

        return self.client.trace(
            name=name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )

    def log_generation(
        self,
        trace,
        name: str,
        model: str,
        input_text: str,
        output_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Записать generation в trace.

        Args:
            trace: Объект trace.
            name: Имя generation.
            model: Название модели.
            input_text: Входной текст.
            output_text: Выходной текст.
            metadata: Дополнительные метаданные.
        """
        if not self.is_enabled() or not trace:
            return

        trace.generation(
            name=name,
            model=model,
            input=input_text,
            output=output_text,
            metadata=metadata or {},
        )

    def log_score(
        self,
        trace,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ):
        """Записать score в trace.

        Args:
            trace: Объект trace.
            name: Название score.
            value: Значение score.
            comment: Необязательный комментарий.
        """
        if not self.is_enabled() or not trace:
            return

        trace.score(
            name=name,
            value=value,
            comment=comment,
        )

    def log_event(
        self,
        trace,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Записать event в trace.

        Args:
            trace: Объект trace.
            name: Название event.
            metadata: Метаданные event.
        """
        if not self.is_enabled() or not trace:
            return

        trace.event(
            name=name,
            metadata=metadata or {},
        )


# Глобальный клиент трассировки.
_tracing_client = None


def get_tracing_client() -> TracingClient:
    """Получить глобальный клиент трассировки (паттерн singleton).

    Returns:
        Экземпляр TracingClient.
    """
    global _tracing_client
    if _tracing_client is None:
        _tracing_client = TracingClient()
    return _tracing_client
