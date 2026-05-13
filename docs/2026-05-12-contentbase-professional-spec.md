# ContentBase — Professional Technical Specification

**Project:** ContentBase  
**Course:** OTUS LLM Driven Development  
**Homework scope:** LLM application with API integration, Langfuse monitoring, RAG/vector DB, datasets, experiments, custom evaluator  
**Target environment:** Galya's local mini-PC: Intel Core Ultra 7 155H, 32 GB RAM, 1 TB SSD, Intel Graphics, Windows 11 Pro  
**Primary delivery:** GitHub repository + notebook/application + Langfuse screenshots/report  
**Version:** 1.1  
**Date:** 2026-05-12

---

## 1. Executive Summary

ContentBase is a local-first multi-agent RAG system for building a thematic knowledge base and using it for summarization, semantic search, and content generation. The system ingests local documents, chunks them, generates embeddings, indexes them in a vector database, retrieves relevant context for user queries, generates grounded answers/content with a local Ollama LLM, and logs the full execution lifecycle to Langfuse.

The project is designed to satisfy two OTUS homework tracks:

1. LLM application with Langfuse monitoring, datasets, experiments, custom evaluator.
2. RAG system with vector DB indexing/search and analysis of retrieval performance/parameters.

---

## 2. Product Goals

### 2.1. User goal

Create a practical local tool for collecting materials on a topic, turning them into a searchable knowledge base, and generating grounded summaries/content from them.

### 2.2. Educational goal

Demonstrate professional use of:

- local LLM via Ollama;
- RAG architecture;
- vector database search;
- Langfuse observability;
- traces, spans, generations, events, scores;
- Langfuse datasets and experiments;
- custom evaluator;
- reproducible Python project structure;
- GitHub-based delivery.

---

## 3. Non-Goals for MVP

The MVP will not implement:

- production auth;
- multi-user SaaS deployment;
- autonomous web crawling;
- large-scale distributed ingestion;
- fine-tuning;
- Kubernetes;
- complex UI beyond notebook/optional Streamlit;
- full agent planning loops;
- REST API endpoints (roadmap item, not MVP blocker).

These are roadmap items, not MVP blockers.

---

## 4. Local Development Environment

### 4.1. Required software on Windows

Install on Galya's local PC:

1. Windows 11 Pro updates.
2. WSL2 with Ubuntu 24.04 or Ubuntu 22.04.
3. Docker Desktop with WSL2 backend.
4. Git for Windows.
5. GitHub CLI (`gh`).
6. Zed IDE for Windows.
7. Python 3.11/3.12 inside WSL2.
8. `uv` package manager inside WSL2.
9. Ollama for Windows or via Docker Desktop (Ollama container).
10. Optional but recommended: VS Code as fallback for Jupyter/WSL notebooks.

### 4.2. IDE decision

Primary IDE: **Zed**.

Reason:

- modern fast editor;
- official Windows build exists;
- suitable for Python project editing;
- good Git workflow;
- can be used for docs/spec/code.

Fallback IDE: **VS Code**.

Reason:

- stronger WSL/Jupyter ecosystem;
- useful if Zed has limitations with notebooks or WSL integration.

Practical recommendation: use Zed for code/docs, keep VS Code installed for Jupyter/WSL debugging if needed.

---

## 5. Model Selection

### 5.1. Local generation model

Primary model:

```bash
ollama pull qwen2.5:14b
```

Rationale:

- strong quality vs local footprint;
- approx. 9 GB model size in Ollama;
- good Russian support;
- good instruction following;
- strong enough for summarization, RAG answers, content generation;
- more practical than qwen3:30b on a 32 GB RAM workstation.

### 5.2. Embedding model

Primary embedding model:

```bash
ollama pull bge-m3
```

Rationale:

- multilingual;
- suitable for Russian/English RAG;
- designed for retrieval;
- works well with Qdrant.

### 5.3. Model configuration

`.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=bge-m3
```

---

## 6. Technical Architecture

```text
User
  |
  v
Notebook / CLI / optional Streamlit UI
  |
  +--> Ingestion Agent
  |      - reads local markdown/txt files
  |      - normalizes text
  |      - emits Langfuse events
  |
  +--> Chunking Agent
  |      - splits documents into chunks
  |      - preserves metadata
  |
  +--> Indexing Agent
  |      - calls Ollama embeddings
  |      - writes vectors to Qdrant
  |
  +--> Retrieval Agent
  |      - embeds query
  |      - searches Qdrant
  |      - returns top-k chunks
  |
  +--> Generation Agent
  |      - builds grounded prompt
  |      - calls qwen2.5:14b via Ollama
  |      - returns answer with sources
  |
  +--> Summarization Agent
  |      - summarizes selected documents/chunks
  |
  +--> Evaluation Agent
  |      - computes custom scores
  |      - runs dataset experiment
  |
  +--> Langfuse Client
         - traces
         - spans
         - generations
         - events
         - scores
```

---

## 7. Infrastructure Components

### 7.1. Docker services

Local Docker Compose includes:

- Qdrant for vector DB;
- Langfuse stack locally (PostgreSQL, ClickHouse, Redis/Valkey, MinIO).

**Langfuse is local-only for this project** (fallback to Langfuse Cloud if local setup becomes too time-consuming, but primary approach is local).

### 7.2. Ports

Recommended ports:

- Ollama: `http://localhost:11434`;
- Qdrant: `http://localhost:6333`;
- Langfuse: `http://localhost:3000`;
- optional Streamlit: `http://localhost:8501`.

---

## 8. Repository Structure

```text
contentbase/
  README.md
  pyproject.toml
  uv.lock
  .env.example
  .gitignore
  docker-compose.yml

  data/
    raw/
      sample_llmops.md
      sample_rag.md
      sample_agents.md
    processed/

  notebooks/
    01_contentbase_demo.ipynb
    02_langfuse_dataset_experiment.ipynb

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
    specification.md
    architecture.md
    report.md
    setup_windows.md
    screenshots/
      traces_overview.png
      trace_detail.png
      observation.png
      dashboards.png
      dataset_experiment.png
      custom_evaluator.png
```

---

## 9. Functional Requirements

### FR-1. Document ingestion

The system shall load `.md` and `.txt` documents from `data/raw/`.

**Metadata sources:**

- `doc_id`: generated from filename (slug: lowercase, replace spaces with underscores, remove special chars)
- `title`: extracted from first H1 heading (# Title) in MD files, or filename as fallback
- `source`: default `course_notes`, can be overridden via `data/raw/<source>/filename.md` folder structure
- `topic`: extracted from subfolder path (e.g., `data/raw/llmops/file.md` → `topic=llmops`)
- `language`: auto-detected via `langdetect` library or from `DEFAULT_LANGUAGE` env var

Acceptance criteria:

- documents are read with UTF-8;
- each document has `doc_id`, `title`, `source`, `topic`, `language`;
- ingestion event is logged to Langfuse.

### FR-2. Chunking

The system shall split documents into overlapping chunks.

**Chunking parameters (character-based for Russian text):**

- `chunk_size_chars = 1200`;
- `chunk_overlap_chars = 200`.

Acceptance criteria:

- chunks preserve document metadata;
- each chunk has stable `chunk_id`;
- tests cover chunk count and overlap behavior.

### FR-3. Embeddings

The system shall generate embeddings via Ollama model `bge-m3`.

Acceptance criteria:

- embeddings are generated for chunks;
- embedding dimensions are stored/validated;
- failures are logged as Langfuse events.

### FR-4. Vector indexing

The system shall store chunks and embeddings in Qdrant.

Acceptance criteria:

- Qdrant collection is created automatically;
- collection uses cosine distance;
- metadata payload is searchable;
- indexing span is visible in Langfuse.

### FR-5. Retrieval

The system shall perform semantic search over Qdrant.

Default parameters:

- `top_k = 5`;
- distance metric: cosine;
- optional metadata filters: `topic`, `source`.

Acceptance criteria:

- query returns top-k chunks with scores;
- retrieved chunks are passed to generation;
- retrieval latency is logged.

### FR-6. RAG answer generation

The system shall generate answers using local Ollama model `qwen2.5:14b`.

Acceptance criteria:

- answer is grounded in retrieved context;
- answer includes sources/chunk references;
- if context is insufficient, answer says so explicitly;
- LLM call is logged as Langfuse generation.

### FR-7. Summarization

The system shall summarize a document or selected chunks.

Acceptance criteria:

- summary includes key points;
- source title is included;
- input/output length is logged;
- compression ratio score is recorded.

### FR-8. Content generation

The system shall generate content drafts based on retrieved knowledge.

Supported content types for MVP:

- short article outline;
- Telegram-style post;
- study note/конспект.

Acceptance criteria:

- generated content includes source references;
- generation mode is logged in metadata.

### FR-9. Langfuse observability

The system shall log:

- traces;
- spans;
- generations;
- events;
- scores;
- metadata;
- user_id and session_id.

Acceptance criteria:

- screenshots prove traces and observations exist;
- at least one detailed trace is documented in report.

### FR-10. Dataset and experiment

The system shall create/use Langfuse dataset `contentbase_rag_eval_v1` with **at least 10 items**.

The system shall create experiment `contentbase_qdrant_top5_baseline`.

Acceptance criteria:

- at least 10 dataset items;
- experiment run is executed;
- results are visible in Langfuse UI.

### FR-11. Custom evaluator

The system shall implement a custom evaluator.

Metrics:

- `answer_relevance`;
- `context_usage`;
- `citation_presence`;
- `honesty_when_unknown`;
- `final_score`.

Acceptance criteria:

- evaluator produces numeric scores;
- scores are sent to Langfuse;
- evaluator code is covered by tests.

---

## 10. Non-Functional Requirements

### NFR-1. Reproducibility

Project shall be runnable from README commands on Windows/WSL2.

### NFR-2. Local-first

Core generation and embeddings shall work through local Ollama.

### NFR-3. Security

Secrets shall not be committed. `.env.example` shall contain placeholders only.

### NFR-4. Testability

Core logic shall have unit tests:

- chunking;
- retrieval result formatting;
- evaluator scoring.

Integration test shall cover end-to-end RAG pipeline.

### NFR-5. Observability

All important operations shall produce Langfuse traces/spans/events.

### NFR-6. Performance

- Retrieval latency: target < 500ms for top_k=5
- Generation latency: acceptable < 30s for summary

---

## 11. Implementation Milestones

### Milestone 1 — Local environment

- Install WSL2, Docker Desktop, Git, GitHub CLI, Zed.
- Pull `qwen2.5:14b` and `bge-m3`.
- Verify Ollama responses.

### Milestone 2 — Repository skeleton

- Create GitHub repository `contentbase`.
- Create Python project with `uv`.
- Add README, .env.example, Docker Compose.

### Milestone 3 — RAG core

- Implement ingestion, chunking, embeddings, Qdrant indexing, retrieval.
- Add tests.

### Milestone 4 — Generation and summarization

- Implement RAG answer generation.
- Implement document summarization.
- Implement content generation mode.

### Milestone 5 — Langfuse tracing

- Add tracing wrapper.
- Add spans/events/generations/scores.
- Verify in UI.

### Milestone 6 — Dataset/evaluator/report

- Create dataset with at least 10 items.
- Create experiment `contentbase_qdrant_top5_baseline`.
- Run experiment.
- Implement evaluator.
- Capture screenshots.
- Write report.

---

## 12. Git Workflow

Recommended:

```bash
git checkout -b feat/project-bootstrap
git commit -m "chore: bootstrap contentbase project"

git checkout -b feat/rag-core
git commit -m "feat: add document ingestion and chunking"
git commit -m "feat: add qdrant vector indexing and retrieval"

git checkout -b feat/langfuse-observability
git commit -m "feat: add langfuse tracing and scores"

git checkout -b feat/evaluation
git commit -m "feat: add dataset experiment and custom evaluator"
```

For homework, a clean `main` branch is enough, but feature branches make the repo look more professional.

---

## 13. Definition of Done

The homework is ready when:

- repository is public or accessible for review;
- README explains local setup;
- local Ollama model is used;
- RAG demo works;
- Qdrant contains indexed documents;
- Langfuse has visible traces;
- at least one detailed trace is screenshoted;
- dataset `contentbase_rag_eval_v1` exists with at least 10 items;
- experiment `contentbase_qdrant_top5_baseline` exists;
- custom evaluator exists;
- report includes screenshots and analysis;
- no secrets are committed.

---

## 14. Recommended First Commands on Galya's PC

PowerShell as Administrator:

```powershell
wsl --install -d Ubuntu-24.04
```

After reboot and Ubuntu setup:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl build-essential python3 python3-venv python3-pip
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Windows apps:

- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Zed: https://zed.dev/download
- Git for Windows: https://git-scm.com/download/win
- GitHub CLI: https://cli.github.com/
- Ollama: https://ollama.com/download (or via Docker Desktop)

Then:

```powershell
ollama pull qwen2.5:14b
ollama pull bge-m3
ollama run qwen2.5:14b
```
