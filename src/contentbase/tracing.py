"""Трассировка ContentBase через Langfuse.

Модуль использует актуальный Langfuse SDK v4 и оставляет приложение рабочим,
если Langfuse не настроен или недоступен.
"""
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

try:
    import langfuse as _langfuse

    LANGFUSE_AVAILABLE = True
except ImportError:
    _langfuse = None  # type: ignore[assignment]
    LANGFUSE_AVAILABLE = False

from contentbase.config import get_settings


@contextmanager
def _null_propagate_attributes(**_: Any) -> Iterator[None]:
    yield


class TracingClient:
    """Клиент трассировки Langfuse."""

    def __init__(self):
        self.settings = get_settings()
        self.client: Any = None

        if LANGFUSE_AVAILABLE and self.settings.langfuse_public_key:
            try:
                self.client = _langfuse.Langfuse(  # type: ignore[union-attr]
                    public_key=self.settings.langfuse_public_key,
                    secret_key=self.settings.langfuse_secret_key,
                    host=self.settings.langfuse_host,
                )
                print("Langfuse tracing initialized")
            except Exception as exc:
                print(f"Failed to initialize Langfuse: {exc}")
                self.client = None
        else:
            print("Langfuse not configured or not available")

    def is_enabled(self) -> bool:
        """Проверить, включена ли трассировка."""
        return self.client is not None

    @contextmanager
    def trace(
        self,
        name: str,
        *,
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Iterator[Any]:
        """Создать корневой trace/span для операции приложения."""
        if not self.is_enabled():
            yield None
            return

        trace_metadata = self._string_metadata(metadata or {})
        with self.client.start_as_current_observation(  # type: ignore[union-attr]
            name=name,
            as_type="span",
            input=input_data,
            metadata=metadata or {},
        ) as observation:
            propagate = (
                _langfuse.propagate_attributes  # type: ignore[union-attr]
                if _langfuse
                else _null_propagate_attributes
            )
            with propagate(
                user_id=user_id,
                session_id=session_id,
                metadata=trace_metadata,
                tags=tags,
                trace_name=name,
            ):
                try:
                    yield observation
                finally:
                    self.flush()

    @contextmanager
    def span(
        self,
        name: str,
        *,
        input_data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        as_type: str = "span",
    ) -> Iterator[Any]:
        """Создать observation/span внутри текущего trace."""
        if not self.is_enabled():
            yield None
            return

        with self.client.start_as_current_observation(  # type: ignore[union-attr]
            name=name,
            as_type=as_type,  # type: ignore[arg-type]
            input=input_data,
            metadata=metadata or {},
        ) as observation:
            yield observation

    @contextmanager
    def generation(
        self,
        name: str,
        *,
        model: str,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        model_parameters: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Any]:
        """Создать generation observation для вызова LLM."""
        if not self.is_enabled():
            yield None
            return

        with self.client.start_as_current_observation(  # type: ignore[union-attr]
            name=name,
            as_type="generation",
            input=input_data,
            model=model,
            model_parameters=model_parameters or {},
            metadata=metadata or {},
        ) as observation:
            yield observation

    def update_current_span(
        self,
        *,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        level: Optional[str] = None,
        status_message: Optional[str] = None,
    ) -> None:
        """Обновить текущий span."""
        if not self.is_enabled():
            return

        self.client.update_current_span(  # type: ignore[union-attr]
            output=output,
            metadata=metadata,
            level=level,  # type: ignore[arg-type]
            status_message=status_message,
        )

    def update_current_generation(
        self,
        *,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        usage_details: Optional[Dict[str, int]] = None,
    ) -> None:
        """Обновить текущий generation observation."""
        if not self.is_enabled():
            return

        self.client.update_current_generation(  # type: ignore[union-attr]
            output=output,
            metadata=metadata,
            usage_details=usage_details,
        )

    def log_event(
        self,
        name: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        level: str = "DEFAULT",
    ) -> None:
        """Записать событие как короткий span-observation.

        В Langfuse SDK v4 отдельного публичного event helper нет, поэтому событие
        отправляется как observation с metadata.event=true.
        """
        if not self.is_enabled():
            return

        with self.span(
            name=name,
            metadata={"event": True, **(metadata or {})},
        ):
            self.update_current_span(level=level)

    def log_score(
        self,
        name: str,
        value: float,
        *,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Записать score на текущий trace."""
        if not self.is_enabled():
            return

        self.client.score_current_trace(  # type: ignore[union-attr]
            name=name,
            value=value,
            data_type="NUMERIC",
            comment=comment,
            metadata=metadata or {},
        )

    def set_current_trace_io(self, *, input_data: Any = None, output_data: Any = None) -> None:
        """Записать input/output текущего trace."""
        if not self.is_enabled():
            return

        self.client.set_current_trace_io(  # type: ignore[union-attr]
            input=input_data,
            output=output_data,
        )

    def flush(self) -> None:
        """Дождаться отправки буфера Langfuse."""
        if self.is_enabled():
            self.client.flush()  # type: ignore[union-attr]

    def _string_metadata(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """Подготовить trace-level metadata для propagate_attributes.

        Langfuse ограничивает propagated metadata ASCII-строками до 200 символов.
        Подробные dict/list остаются в observation metadata.
        """
        result = {}
        for key, value in metadata.items():
            text = str(value)
            if text.isascii():
                result[str(key)] = text[:200]
        return result


_tracing_client = None


def get_tracing_client() -> TracingClient:
    """Получить singleton-клиент трассировки."""
    global _tracing_client
    if _tracing_client is None:
        _tracing_client = TracingClient()
    return _tracing_client
