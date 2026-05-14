# ContentBase

ContentBase - учебный Python-проект для локальной обработки текстовых документов с помощью LLM. Проект ориентирован на работу с русскоязычными материалами и демонстрирует базовые элементы будущей RAG-системы: загрузку документов, разбиение на фрагменты, генерацию ответов и кратких пересказов.

Проект подготовлен в рамках курса OTUS «LLM Driven Development».

## Возможности

- загрузка `.md` и `.txt` документов из файла или директории;
- извлечение базовых метаданных документа;
- разбиение текста на чанки с перекрытием;
- краткий пересказ документа через Ollama;
- ответы на вопросы с контекстом из файла или директории;
- режим mock-ответов, если Ollama недоступна;
- CLI-интерфейс на Typer;
- интеграция с Langfuse: traces, spans, events, generations, metadata, scores, user_id/session_id;
- custom evaluator для оценки ответов;
- LLM-as-a-judge режим для дополнительной оценки качества;
- Docker Compose для запуска Qdrant как задела под следующий этап RAG.

## Текущее состояние

Сейчас реализован первый этап проекта:

1. Загрузка документов.
2. Разбиение документов на чанки.
3. Саммаризация.
4. Q&A по полному контексту файла или директории.
5. Трассировка Langfuse для ingestion, summarization и Q&A.
6. Custom evaluator и score-запись в Langfuse.
7. Базовые тесты для чанкинга и генерации с контекстом.

Полноценный RAG с векторным поиском через Qdrant находится в плане развития. Настройки Qdrant уже есть в конфигурации и `docker-compose.yml`, но CLI-команда `query` пока не выполняет семантический поиск по векторной базе.

## Требования

- Python 3.11 или новее;
- `uv`;
- Ollama для реальной генерации ответов;
- Docker и Docker Compose, если нужен Qdrant;
- модели Ollama:
  - `qwen2.5:14b` для генерации;
  - `bge-m3` для эмбеддингов на будущих этапах.

## Установка

```bash
git clone git@github.com:GalinaErshova/contentbase.git
cd contentbase
uv sync
```

Если проект уже скачан локально:

```bash
cd /home/projects/contentbase
uv sync
```

## Подготовка Ollama

Запустите Ollama и загрузите модель для генерации:

```bash
ollama pull qwen2.5:14b
```

Для будущего RAG-режима можно также загрузить embedding-модель:

```bash
ollama pull bge-m3
```

Если Ollama недоступна, приложение автоматически перейдет в mock-режим. Это удобно для тестов и демонстрации CLI, но ответы будут шаблонными.

## Настройка окружения

Основные настройки читаются из переменных окружения или файла `.env`.

Пример:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=bge-m3
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=contentbase
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
DEFAULT_LANGUAGE=ru
LOG_LEVEL=INFO
```

Langfuse необязателен. Если ключи не указаны, приложение продолжит работать без отправки трассировок.

## Запуск инфраструктуры

Для запуска Qdrant:

```bash
docker compose up -d
```

Qdrant будет доступен на:

```text
http://localhost:6333
```

Остановить контейнеры:

```bash
docker compose down
```

## Использование

Посмотреть доступные команды:

```bash
uv run python -m contentbase.app --help
```

Или через установленный entrypoint:

```bash
uv run contentbase --help
```

### Проверить статус

```bash
uv run python -m contentbase.app status
```

Команда покажет настройки Ollama, Qdrant, Langfuse и приложения.

### Загрузить и разбить документы на чанки

```bash
uv run python -m contentbase.app ingest data/raw
```

С подробным выводом:

```bash
uv run python -m contentbase.app ingest data/raw --verbose
```

### Сделать краткий пересказ документа

```bash
uv run python -m contentbase.app summarize data/raw/sample_01_rag.md
```

С дополнительной информацией:

```bash
uv run python -m contentbase.app summarize data/raw/sample_01_rag.md --verbose
```

### Ответить на вопрос без контекста

```bash
uv run python -m contentbase.app query --question "Что такое RAG?"
```

### Ответить на вопрос с контекстом из файла

```bash
uv run python -m contentbase.app query \
  --question "Что такое RAG?" \
  --input data/raw/sample_01_rag.md
```

### Ответить на вопрос с контекстом из директории

```bash
uv run python -m contentbase.app query \
  --question "Какие темы описаны в документах?" \
  --input data/raw
```

### Ответить на вопрос и записать Langfuse scores

```bash
uv run python -m contentbase.app query \
  --question "Что такое RAG и зачем он нужен?" \
  --input data/raw/sample_01_rag.md \
  --verbose \
  --user-id demo-galina \
  --session-id homework-demo
```

### Запустить LLM-as-a-judge

```bash
uv run python -m contentbase.app query \
  --question "Какие преимущества дает RAG?" \
  --input data/raw/sample_01_rag.md \
  --llm-judge \
  --user-id demo-galina \
  --session-id homework-demo
```

## Структура проекта

```text
contentbase/
├── data/
│   └── raw/                    # Пример исходных документов
├── docs/
│   └── screenshots/            # Скриншоты Langfuse для сдачи
├── src/
│   └── contentbase/
│       ├── app.py              # CLI-приложение
│       ├── chunking.py         # Разбиение текста на чанки
│       ├── config.py           # Настройки приложения
│       ├── evaluation.py       # Custom evaluator и LLM-as-a-judge helpers
│       ├── generation.py       # Генерация ответов через Ollama или mock-клиент
│       ├── ingestion.py        # Загрузка документов
│       ├── schemas.py          # Pydantic-модели
│       ├── summarization.py    # Саммаризация документов
│       └── tracing.py          # Обертки для Langfuse
├── tests/                      # Автотесты
├── docker-compose.yml          # Qdrant и заготовка для Langfuse
├── pyproject.toml              # Зависимости и настройки проекта
└── README.md
```

## Тесты и качество кода

Запустить тесты:

```bash
uv run pytest
```

Проверить код через Ruff:

```bash
uv run ruff check src tests
```

Проверить типы:

```bash
uv run mypy src
```

## Наблюдаемость

В проекте есть поддержка Langfuse. Если задать `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` и `LANGFUSE_HOST`, операции загрузки документов, саммаризации и генерации ответов будут отправлять traces.

Что пишется в Langfuse:

- root trace для CLI-команды;
- spans для загрузки документов, загрузки контекста, чанкинга и сборки prompt;
- generation observations для вызовов Ollama;
- event-подобные observations для старта, завершения и ошибок;
- metadata: режим, файл контекста, источники, длины входа/выхода, mock-mode;
- `user_id` и `session_id` через CLI-опции;
- scores от custom evaluator;
- score `llm_as_judge_score`, если включен `--llm-judge`.

Если Langfuse не настроен, приложение работает без него.

Локальный чеклист сдачи можно вести в `docs/homework-submission.md`; этот файл намеренно не коммитится, чтобы не смешивать учебные заметки с кодом проекта.

## Планы развития

- подключить Qdrant к пайплайну ingestion;
- сохранять чанки и эмбеддинги в векторную базу;
- добавить семантический поиск по документам;
- реализовать полноценный RAG-режим для команды `query`;
- добавить оценку качества ответов;
- расширить интеграцию с Langfuse.
