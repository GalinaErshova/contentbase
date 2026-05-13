# ContentBase — Техническое задание для ДЗ OTUS LLM Driven Development

> **Для agentic workers:** REQUIRED SUB-SKILL: Используй `subagent-driven-development` или `executing-plans` для реализации плана task-by-task.

**Версия:** 0.2  
**Дата:** 2026-05-12  
**Автор идеи:** Галя  
**Проект:** ContentBase  
**Контекст:** ДЗ курса OTUS «LLM Driven Development», занятия про LangChain, LlamaIndex, Ollama, Haystack, Langfuse, RAG и агентные системы.

---

## 1. Краткое описание

**ContentBase** — локальное LLM/RAG-приложение, которое помогает собирать базу знаний по выбранной тематике, индексировать материалы, делать саммаризацию, искать по базе и генерировать контент на основе найденных источников.

Проект проектируется как **мульти-агентная система**, но в первой учебной версии реализуется минимальный, устойчивый и проверяемый MVP, достаточный для сдачи ДЗ:

1. загрузка документов;
2. разбиение на чанки;
3. создание эмбеддингов;
4. индексация в векторной БД;
5. RAG-поиск;
6. генерация ответа/саммари;
7. трассировка в Langfuse;
8. тестовый dataset (минимум 10 items) и evaluator в Langfuse;
9. скриншоты Langfuse UI для отчёта.

---

## 2. Можно ли выполнить локально на имеющемся ПК

Да, проект можно выполнить локально на мини-ПК:

- CPU: Intel Core Ultra 7 155H;
- RAM: 32 ГБ;
- SSD: 1 ТБ;
- GPU: Intel Graphics;
- OS: Windows 11 Pro.

Рекомендуемый режим разработки:

- Windows 11 Pro + WSL2;
- Docker Desktop with WSL2 backend;
- Python внутри WSL2;
- Langfuse локально через Docker Compose;
- Ollama локально через Docker Desktop или native Windows installation;
- приложение ContentBase локально как Jupyter Notebook / Python CLI / Streamlit UI.

Для учебного проекта 32 ГБ RAM достаточно. Большие локальные LLM запускать необязательно: можно использовать OpenAI API или другой внешний LLM API, а локально держать Langfuse, векторную БД и само приложение.

---

## 3. Цель проекта

Создать учебное LLM-приложение, демонстрирующее:

- интеграцию LLM с внешней базой знаний;
- построение RAG-пайплайна;
- использование векторной БД;
- трассировку операций через Langfuse;
- работу с traces, spans, generations, events, scores;
- создание dataset и эксперимента в Langfuse;
- использование evaluator для оценки качества ответов;
- базовую архитектуру мульти-агентной системы.

---

## 4. Выбранный сценарий

**Сценарий:** тематическая база знаний для генерации контента.

Пользователь задаёт тему, например:

- LLMOps;
- LangChain и агенты;
- RAG-системы;
- генеративное искусство;
- документация по конкретному проекту;
- материалы курса.

Система должна:

1. принимать документы по теме;
2. извлекать текст;
3. сохранять документы и метаданные;
4. строить индекс;
5. отвечать на вопросы по базе;
6. делать краткие саммари;
7. генерировать черновики контента на основе найденных источников;
8. показывать, какие источники были использованы;
9. логировать весь пайплайн в Langfuse.

---

## 5. Scope MVP для сдачи ДЗ

### 5.1. Обязательно реализовать

#### Приложение

- Python-проект в стиле образовательных workshop-репозиториев.
- Один основной сценарий запуска:
  - Jupyter Notebook `notebooks/contentbase_demo.ipynb`; или
  - CLI `python -m contentbase.app`; или
  - простой Streamlit UI.
- Загрузка локальных `.txt` / `.md` документов.
- Чанкинг документов.
- Эмбеддинги.
- Индексация в векторной БД.
- Семантический поиск top-k.
- Генерация ответа на вопрос с цитированием найденных фрагментов.
- Саммаризация выбранного документа или набора документов.

#### Langfuse

- **Локальный Langfuse через Docker Compose** (основной вариант).
- Fallback: Langfuse Cloud если локальная настройка займёт слишком много времени.
- Создание проекта и API-ключей.
- Интеграция Langfuse SDK.
- Логирование:
  - trace на каждый пользовательский запрос;
  - spans для загрузки, чанкинга, retrieval, generation;
  - generation для LLM-вызова;
  - events для загрузки файла, ошибок, старта/завершения пайплайна;
  - scores для оценки качества ответа.
- Передача metadata:
  - user_id;
  - session_id;
  - dataset/topic name;
  - vector_db;
  - embedding_model;
  - llm_model;
  - top_k;
  - latency;
  - token usage, если доступно;
  - estimated cost, если доступно.

#### Dataset и evaluator

- Создать тестовый dataset `contentbase_rag_eval_v1` в Langfuse.
- **Минимум 10 тестовых вопросов** с ожидаемыми ответами / критериями.
- Создать эксперимент `contentbase_qdrant_top5_baseline`.
- Запустить эксперимент.
- Реализовать custom evaluator для кейса ContentBase.
- Оценивать минимум:
  - answer_relevance;
  - context_usage;
  - groundedness / citation_presence.

#### Отчёт

- README с инструкцией запуска.
- Краткое описание архитектуры.
- Скриншоты Langfuse:
  - traces общий вид;
  - один детальный trace в развёрнутом формате;
  - observation;
  - dashboards;
  - dataset / experiment;
  - custom evaluator;
  - по возможности llm-as-a-judge и annotations queue.

---

## 6. Что можно НЕ реализовывать в MVP

Чтобы уложиться в ДЗ, в первой версии можно не делать:

- полноценный веб-краулер;
- автоматическую загрузку из Telegram/YouTube/сайтов;
- сложный multi-agent orchestration;
- роли агентов с автономным планированием;
- fine-tuning;
- авторизацию пользователей;
- production deployment;
- сравнение нескольких LLM;
- большой датасет 1000+ документов;
- полноценный human-in-the-loop UI;
- REST API endpoints (roadmap item, не часть MVP).

Эти функции можно описать как roadmap.

---

## 7. Архитектура

### 7.1. Компоненты

```text
User
  |
  v
ContentBase App / Notebook / Streamlit
  |
  +--> Ingestion Agent
  |      - читает документы
  |      - чистит текст
  |      - создаёт чанки
  |
  +--> Indexing Agent
  |      - создаёт эмбеддинги
  |      - пишет в vector DB
  |
  +--> Retrieval Agent
  |      - ищет релевантные чанки
  |      - применяет top-k и фильтры
  |
  +--> Summarization Agent
  |      - делает краткое содержание
  |
  +--> Content Generation Agent
  |      - генерирует ответ / пост / конспект
  |
  +--> Evaluation Agent
  |      - считает custom scores
  |      - запускает dataset experiment
  |
  +--> Langfuse
         - traces
         - spans
         - generations
         - events
         - scores
         - datasets
         - experiments
```

### 7.2. Агентность в MVP

В MVP агенты могут быть реализованы как отдельные Python-классы или функции, без сложного автономного поведения.

Пример:

- `IngestionAgent`;
- `IndexingAgent`;
- `RetrieverAgent`;
- `SummarizerAgent`;
- `GeneratorAgent`;
- `EvaluatorAgent`.

Это позволит показать мульти-агентную архитектуру, но не перегрузить проект.

---

## 8. Рекомендуемый tech stack

### 8.1. Базовый стек

- Python 3.11 или 3.12;
- uv или Poetry для зависимостей;
- Jupyter Notebook для демонстрации;
- LangChain или LlamaIndex для RAG-пайплайна;
- Langfuse SDK для мониторинга;
- Docker Desktop + WSL2;
- GitHub для сдачи.

### 8.2. LLM

Вариант A, самый простой для ДЗ:

- OpenAI GPT через API.

Вариант B, локальный/гибридный:

- Ollama для локальных моделей;
- OpenAI-compatible endpoint;
- внешняя LLM только для evaluator / judge.

Рекомендация для стабильной сдачи: использовать внешний LLM API для генерации, а локально держать инфраструктуру.

### 8.3. Embeddings

Варианты:

- OpenAI embeddings;
- sentence-transformers локально;
- BAAI/bge-small или bge-m3;
- intfloat/multilingual-e5-small.

Для русскоязычных материалов лучше взять multilingual embedding model или OpenAI embeddings.

### 8.4. Vector DB

Для ДЗ с фокусом на векторную БД рекомендованы варианты:

#### Вариант 1: Qdrant

Плюсы:

- просто запускается в Docker;
- есть HNSW;
- хорошая Python-интеграция;
- удобно показать фильтрацию по метаданным;
- подходит для локального Windows/WSL2.

Минусы:

- меньше вариантов ANN-алгоритмов для сравнения, чем в Milvus.

#### Вариант 2: Chroma

Плюсы:

- самый простой старт;
- можно хранить локально без отдельного сервиса.

Минусы:

- менее убедительно для ДЗ про vector DB и ANN trade-offs.

#### Вариант 3: Milvus

Плюсы:

- хорошо подходит под задание про IVF/HNSW/ANNOY и ANN-сравнение.

Минусы:

- тяжелее локально;
- сложнее эксплуатация;
- больше риска потратить время на инфраструктуру.

**Рекомендация для ContentBase MVP:** Qdrant.  
**Рекомендация для расширенного бонуса:** отдельный эксперимент с Milvus или FAISS для сравнения IVF/HNSW.

---

## 9. Локальная инфраструктура

### 9.1. Docker-сервисы

Локальный Docker Compose включает:

- Langfuse;
- PostgreSQL для Langfuse;
- ClickHouse для Langfuse;
- Redis / Valkey;
- MinIO;
- Qdrant;
- Ollama (опционально, через Docker Desktop).

Использовать официальный `docker-compose.yml` Langfuse и добавить отдельный Qdrant service.

### 9.2. Порты

Предлагаемые порты:

- Langfuse UI: `http://localhost:3000`;
- Qdrant: `http://localhost:6333`;
- MinIO console: `http://localhost:9090`, если используется стандартный compose Langfuse;
- Ollama: `http://localhost:11434` (через Docker Desktop или native).

---

## 10. Структура репозитория

```text
contentbase/
  README.md
  pyproject.toml
  .env.example
  docker-compose.yml

  data/
    raw/
      sample_01.md
      sample_02.md
    processed/

  notebooks/
    contentbase_demo.ipynb
    langfuse_dataset_experiment.ipynb

  src/
    contentbase/
      __init__.py
      config.py
      schemas.py
      ingestion.py
      chunking.py
      embeddings.py
      vector_store.py
      retrieval.py
      generation.py
      summarization.py
      evaluation.py
      tracing.py
      app.py

  tests/
    test_chunking.py
    test_retrieval.py
    test_evaluation.py
    test_integration.py

  docs/
    architecture.md
    report.md
    screenshots/
      traces_overview.png
      trace_detail.png
      observation.png
      dashboard.png
      dataset_experiment.png
      custom_evaluator.png
```

---

## 11. Основные пользовательские сценарии

### Сценарий 1. Индексация документов

1. Пользователь кладёт `.md` или `.txt` файлы в `data/raw/`.
2. Запускает ingestion.
3. Система читает документы.
4. Система режет текст на чанки.
5. Система создаёт эмбеддинги.
6. Система сохраняет чанки в Qdrant с метаданными.
7. Langfuse получает trace `document_ingestion`.

### Сценарий 2. Вопрос по базе знаний

1. Пользователь задаёт вопрос.
2. Система создаёт embedding вопроса.
3. Retrieval Agent ищет top-k чанков.
4. Generation Agent формирует ответ с контекстом.
5. Ответ содержит краткие ссылки на источники.
6. Langfuse получает trace `rag_query`.
7. Evaluator Agent пишет score.

### Сценарий 3. Саммаризация

1. Пользователь выбирает документ или тему.
2. Система получает релевантные чанки.
3. Summarization Agent создаёт summary.
4. Langfuse логирует generation и метрики:
   - input length;
   - output length;
   - compression ratio;
   - latency.

### Сценарий 4. Генерация контента

1. Пользователь просит: «Сделай пост/конспект/план статьи по теме X».
2. Retrieval Agent достаёт материалы.
3. Generator Agent создаёт контент.
4. Ответ содержит использованные источники.
5. Langfuse логирует trace `content_generation`.

---

## 12. Данные для MVP

Рекомендуемый учебный набор:

- 5–10 markdown-документов по теме LLMOps/RAG/агентов;
- можно взять материалы курса, свои заметки, README из workshop-проектов;
- общий объём: 20–100 страниц текста достаточно.

Метаданные документа:

```json
{
  "doc_id": "llmops_intro_001",
  "title": "Введение в LLMOps",
  "source": "course_notes",
  "topic": "llmops",
  "language": "ru",
  "created_at": "2026-05-12"
}
```

**Источники метаданных:**

- `doc_id`: генерируется из filename (slug: lowercase, заменить пробелы на подчёркивания, убрать спецсимволы)
- `title`: берётся из первой строки заголовка H1 (# Title) в MD файлах, или filename как fallback
- `source`: по умолчанию `"course_notes"`, можно переопределить через структуру папок `data/raw/<source>/filename.md`
- `topic`: берётся из подпапки (например, `data/raw/llmops/file.md` → `topic="llmops"`)
- `language`: автоопределение через библиотеку `langdetect` или из переменной `DEFAULT_LANGUAGE` в .env

Метаданные чанка:

```json
{
  "chunk_id": "llmops_intro_001_chunk_0001",
  "doc_id": "llmops_intro_001",
  "title": "Введение в LLMOps",
  "topic": "llmops",
  "chunk_index": 1,
  "source": "course_notes"
}
```

---

## 13. Требования к RAG

### 13.1. Chunking

**Параметры чанкинга (символы, оптимально для русского текста):**

- размер чанка: **1200 символов**;
- overlap: **200 символов**;
- сохранять `doc_id`, `chunk_id`, `title`, `source`, `topic`.

### 13.2. Retrieval

- top-k по умолчанию: 5;
- similarity: cosine;
- фильтрация по `topic` и/или `source`;
- вывод score для каждого найденного чанка.

### 13.3. Generation

Ответ должен включать:

- прямой ответ на вопрос;
- краткое объяснение;
- список использованных источников/чанков;
- если данных недостаточно — честное сообщение, что база знаний не содержит ответа.

---

## 14. Требования к Langfuse-интеграции

### 14.1. Trace names

- `document_ingestion`;
- `rag_query`;
- `document_summary`;
- `content_generation`;
- `dataset_experiment_run`.

### 14.2. Spans

Для `rag_query`:

1. `prepare_query`;
2. `embed_query`;
3. `retrieve_context`;
4. `build_prompt`;
5. `llm_generation`;
6. `evaluate_answer`.

### 14.3. Events

- `document_uploaded`;
- `chunks_created`;
- `vector_index_updated`;
- `retrieval_no_results`;
- `generation_error`;
- `evaluation_completed`.

### 14.4. Scores

Минимальные custom scores:

- `answer_relevance`: 0–1;
- `context_usage`: 0–1;
- `citation_presence`: 0 или 1;
- `latency_ms`: числовое значение;
- `retrieved_docs_count`: числовое значение.

---

## 15. Dataset и experiment в Langfuse

### 15.1. Dataset

Название: `contentbase_rag_eval_v1`.

**Минимум 10 items** (увеличено с 5 для лучшей демонстрации):

```json
{
  "input": {
    "question": "Что такое RAG и зачем он нужен?",
    "topic": "rag"
  },
  "expected_output": {
    "must_include": ["retrieval", "generation", "внешние знания"],
    "must_cite_sources": true
  }
}
```

### 15.2. Experiment

Название: `contentbase_qdrant_top5_baseline`.

Параметры:

```json
{
  "vector_db": "qdrant",
  "embedding_model": "bge-m3",
  "llm_model": "qwen2.5:14b",
  "top_k": 5,
  "chunk_size": 1200,
  "chunk_overlap": 200
}
```

### 15.3. Custom evaluator

Evaluator должен проверять:

1. есть ли ответ;
2. содержит ли ответ ссылки/источники;
3. использует ли ответ найденный контекст;
4. содержит ли ключевые слова из expected_output;
5. не отвечает ли система на вопрос вне базы слишком уверенно.

Пример score:

```text
final_score = 0.4 * answer_relevance + 0.3 * context_usage + 0.2 * citation_presence + 0.1 * safety_honesty
```

---

## 16. ANN и анализ векторной БД

Для Qdrant в отчёте описать:

- что используется HNSW;
- какие параметры важны:
  - `m`;
  - `ef_construct`;
  - `hnsw_ef`;
  - distance metric;
- trade-off:
  - выше `ef` → лучше recall, но медленнее поиск;
  - ниже `ef` → быстрее, но может быть хуже качество.

Минимальный эксперимент:

- top_k = 3, 5, 10;
- сравнить latency и субъективное качество;
- показать таблицу результатов в README/report.

Бонус:

- сравнить Qdrant HNSW с FAISS IndexFlat / IVF;
- или поднять Milvus и сравнить IVF vs HNSW.

---

## 17. Acceptance criteria

Проект считается готовым к сдаче, если:

1. Репозиторий запускается по README.
2. Есть `.env.example` без секретов.
3. Есть минимум 5 документов или демонстрационный dataset.
4. Документы индексируются в vector DB.
5. RAG-запрос возвращает ответ и источники.
6. Саммаризация работает минимум для одного документа.
7. Langfuse получает traces.
8. В trace видны spans, generation, events, metadata.
9. Есть dataset `contentbase_rag_eval_v1` в Langfuse (минимум 10 items).
10. Есть experiment `contentbase_qdrant_top5_baseline`.
11. Есть custom evaluator и score.
12. Есть скриншоты Langfuse UI.
13. README объясняет архитектуру, запуск и результаты.
14. Report содержит анализ метрик: latency, retrieval quality, token usage/cost.

---

## 18. Риски и упрощения

### Риск: Langfuse локально может занять время на настройку

Снижение риска:

- **основной вариант: локальный Langfuse через Docker Compose**;
- если займёт слишком много времени — fallback на Langfuse Cloud;
- приложение писать так, чтобы менялись только переменные окружения.

### Риск: локальные LLM могут быть медленными

Снижение риска:

- для генерации использовать OpenAI-compatible API;
- локально запускать только embeddings или только инфраструктуру;
- использовать Ollama через Docker Desktop для стабильности.

### Риск: Milvus тяжёл для локального ДЗ

Снижение риска:

- использовать Qdrant для основного проекта;
- ANN trade-offs описать на HNSW и параметрах поиска;
- Milvus/FAISS сделать бонусом, если останется время.

---

## 19. Roadmap после MVP

### Версия 0.2

- Streamlit UI;
- загрузка PDF;
- annotations queue в Langfuse;
- LLM-as-a-judge evaluator;
- human feedback кнопки 👍/👎;
- REST API endpoints.

### Версия 0.3

- web ingestion;
- загрузка YouTube transcript;
- автоматическое обновление базы знаний;
- отдельный planning agent.

### Версия 0.4

- генерация контент-плана;
- генерация постов/статей;
- редакторский agent;
- fact-checking agent;
- экспорт в Markdown/Obsidian/SilverBullet.

---

## 20. Рекомендуемый порядок реализации

1. Создать репозиторий `contentbase`.
2. Настроить окружение (WSL2, Docker Desktop, Ollama).
3. Реализовать ingestion, chunking, embeddings, vector store.
4. Реализовать retrieval и generation.
5. Добавить Langfuse tracing.
6. Создать dataset (минимум 10 items) и experiment.
7. Реализовать evaluator.
8. Создать демо notebook и отчёт.
9. Подготовить скриншоты Langfuse UI.
10. Сдать ДЗ.

---

## Приложение A: Пример структуры папок для метаданных

```text
data/raw/
  course_notes/
    llmops/
      01_intro.md           → source="course_notes", topic="llmops"
      02_retrieval.md
    rag/
      01_basics.md          → source="course_notes", topic="rag"
  external_articles/
    2024/
      01_llmops_trends.md   → source="external_articles", topic="llmops"
```

---

## Приложение B: Пример .env.example

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=bge-m3

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=contentbase

# Langfuse
LANGFUSE_PUBLIC_KEY=
LANGFU…KEY=
LANGFUSE_HOST=http://localhost:3000

# App
DEFAULT_LANGUAGE=ru
LOG_LEVEL=INFO
```
