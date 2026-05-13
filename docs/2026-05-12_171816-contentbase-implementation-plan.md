# ContentBase Implementation Plan v3

> **Для agentic workers:** REQUIRED SUB-SKILL: Используй `subagent-driven-development` или `executing-plans` для реализации плана task-by-task.

**Goal:** Build a local-first multi-agent RAG application for OTUS homework, using Ollama, Qdrant, Langfuse, Python, and GitHub.

**Development Environment:** Mini-PC 10.66.66.12 with Docker Compose and Ollama already installed.

**Implementation Strategy:**
- **Phase 1**: Basic document processing (read, summarize, Q&A) without vector database
- **Phase 2**: Add vector database and semantic search
- **Phase 3**: Evaluation and homework report

**Architecture:** ContentBase is a modular Python project with separate ingestion, chunking, embedding, vector-store, retrieval, generation, summarization, evaluation, and tracing modules. Local services run via Docker/Ollama; application is demonstrated through notebooks and CLI.

**Tech Stack:** Windows 11 Pro, WSL2 Ubuntu, Docker Desktop, Zed IDE, Git/GitHub, Python 3.11/3.12, uv, Ollama qwen2.5:14b, Ollama bge-m3, Qdrant, Langfuse, pytest, Jupyter.

**Reference Project:** https://github.com/pueraeternis/agentic-rag-workshop (pattern for local RAG + Langfuse)

---

## File Structure

```
contentbase/
├── README.md                       # Professional README with badges, architecture, usage
├── pyproject.toml                  # Python project/dependencies
├── .env.example                    # Safe environment template
├── .gitignore                      # Exclude secrets/data/cache
├── docker-compose.yml               # Qdrant and Langfuse stack (Phase 2+)
├── docs/
│   ├── architecture.md             # Architecture documentation
│   ├── report.md                  # Final homework report
│   ├── setup_windows.md           # Windows/WSL setup guide
│   └── screenshots/               # Langfuse UI screenshots
├── data/
│   └── raw/                      # Source documents (.md, .txt)
├── notebooks/
│   ├── 01_phase1_basic_processing.ipynb    # Phase 1 demo
│   ├── 02_phase2_rag_demo.ipynb           # Phase 2 demo
│   └── 03_langfuse_dataset_experiment.ipynb # Phase 3 demo
├── src/
│   └── contentbase/
│       ├── __init__.py
│       ├── config.py              # Settings loader
│       ├── schemas.py            # Data models (Document, Chunk, etc.)
│       ├── ingestion.py           # Document loading
│       ├── chunking.py          # Chunk splitter
│       ├── embeddings.py         # Ollama embeddings (Phase 2)
│       ├── vector_store.py       # Qdrant operations (Phase 2)
│       ├── retrieval.py          # Search orchestration (Phase 2)
│       ├── generation.py         # RAG answer/content generation
│       ├── summarization.py      # Summary pipeline
│       ├── evaluation.py         # Custom evaluator (Phase 3)
│       ├── tracing.py           # Langfuse wrappers
│       └── app.py              # CLI entry point
└── tests/
    ├── test_chunking.py          # Chunking tests
    ├── test_evaluation.py         # Evaluator tests (Phase 3)
    ├── test_retrieval.py        # Retrieval tests (Phase 2)
    └── test_integration.py      # E2E tests (Phase 3)
```

---

## Phase 0 — Local Workstation Setup (MINIMAL)

**Note:** Development machine (10.66.66.12) already has Docker Compose and Ollama installed.

### Task 0.1: Verify local environment

**Files:** None

- [ ] **Step 1: Verify Docker Compose**

```bash
docker compose version
```

Expected: version printed.

- [ ] **Step 2: Verify Ollama**

```bash
ollama --version
ollama list
```

Expected: version printed, models listed (qwen2.5:14b, bge-m3).

- [ ] **Step 3: Verify WSL2** (if developing from Windows)

```bash
wsl --status
```

Expected: WSL2 is running.

### Task 0.2: Create GitHub repository

**Files:**
- Create local repo folder: contentbase/

- [ ] **Step 1: Authenticate GitHub CLI**

```bash
gh auth login
```

Expected: authenticated GitHub account.

- [ ] **Step 2: Create repository**

```bash
gh repo create contentbase --public --description "Local-first multi-agent RAG knowledge base with Ollama, Qdrant, and Langfuse for OTUS LLM Driven Development course" --clone
cd contentbase
```

Expected: GitHub repo exists and local clone is created.

- [ ] **Step 3: Open in Zed**

```bash
zed .
```

Expected: project opens in Zed.

### Task 0.3: Bootstrap Python project

**Files:**
- Create: pyproject.toml
- Create: .gitignore
- Create: .env.example
- Create: README.md

- [ ] **Step 1: Initialize uv project**

From the repo folder:

```bash
uv init --package contentbase
```

Expected: pyproject.toml created.

- [ ] **Step 2: Add dependencies (Phase 1)**

```bash
uv add langfuse ollama pydantic pydantic-settings python-dotenv rich typer jupyter ipykernel langdetect
uv add --dev pytest ruff mypy
```

Expected: dependencies added and lockfile created.

- [ ] **Step 3: Create .env.example**

```bash
cat > .env.example << 'EOF'
# ContentBase Environment Variables
# Copy this to .env and fill in actual values
# Do not commit .env to Git!

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=bge-m3

# Qdrant Vector Database (Phase 2)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=contentbase

# Langfuse Observability
LANGFUSE_PUBLIC_KEY=
LANGFU…KEY=
LANGFUSE_HOST=http://localhost:3000

# Application Settings
DEFAULT_LANGUAGE=ru
LOG_LEVEL=INFO

# Optional: Langfuse Cloud (fallback if local setup fails)
# LANGFUSE_HOST=https://cloud.langfuse.com
EOF
```

Expected: .env.example created with placeholders.

- [ ] **Step 4: Create .gitignore**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env

# Data
data/processed/
data/cache/

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# Logs
*.log

# OS
.DS_Store
Thumbs.db
EOF
```

Expected: .gitignore created.

- [ ] **Step 5: Create professional README**

Create README.md with:
- Project badges
- Features section
- Architecture overview
- Installation instructions
- Usage examples
- Development guidelines
- Contributing section
- License

(See full README template at end of this plan)

- [ ] **Step 6: Commit bootstrap**

```bash
git add .
git commit -m "chore: bootstrap contentbase project"
git push
```

Expected: first commit is visible on GitHub.

---

## Phase 1 — Basic Document Processing (No Vector Database)

**Goal:** Implement document ingestion, summarization, and Q&A using full document context (no vector search yet).

### Task 1.1: Implement core schemas

**Files:**
- Create: src/contentbase/schemas.py
- Create: tests/test_chunking.py

- [ ] **Step 1: Define data models**

Create Pydantic models:
- Document: doc_id, title, source, topic, language, created_at
- Chunk: chunk_id, doc_id, title, topic, chunk_index, source, text
- RagAnswer: answer, sources, confidence
- EvaluationResult: answer_relevance, context_usage, citation_presence, honesty_when_unknown, final_score

- [ ] **Step 2: Add tests for stable IDs**

Test that chunk IDs are deterministic for same doc/chunk index.

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_chunking.py -v
```

Expected: tests pass after implementation.

- [ ] **Step 4: Commit**

```bash
git add src/contentbase/schemas.py tests/test_chunking.py
git commit -m "feat: add core schemas"
```

### Task 1.2: Implement ingestion and chunking

**Files:**
- Create: src/contentbase/ingestion.py
- Create: src/contentbase/chunking.py
- Modify: tests/test_chunking.py

- [ ] **Step 1: Write failing chunking tests**

Test chunk size (1200 chars), overlap (200 chars), metadata preservation.

- [ ] **Step 2: Implement document loader**

Load .md/.txt from data/raw/, extract metadata:
- doc_id: slug from filename
- title: first H1 or filename
- source: folder name or "course_notes"
- topic: folder name
- language: auto-detect via langdetect

- [ ] **Step 3: Implement chunk splitter**

Split documents into overlapping chunks (1200 chars, 200 overlap).

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/test_chunking.py -v
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add src/contentbase/ingestion.py src/contentbase/chunking.py tests/test_chunking.py
git commit -m "feat: add document ingestion and chunking"
```

### Task 1.3: Implement configuration

**Files:**
- Create: src/contentbase/config.py

- [ ] **Step 1: Implement settings loader**

Load settings from .env using pydantic-settings:
- Ollama settings (base_url, chat_model, embedding_model)
- Qdrant settings (url, collection_name)
- Langfuse settings (public_key, secret_key, host)
- App settings (default_language, log_level)

- [ ] **Step 2: Commit**

```bash
git add src/contentbase/config.py
git commit -m "feat: add configuration loader"
```

### Task 1.4: Implement basic generation

**Files:**
- Create: src/contentbase/generation.py
- Create: src/contentbase/summarization.py

- [ ] **Step 1: Implement Ollama client**

Create wrapper for Ollama API (chat completions).

- [ ] **Step 2: Implement summarization**

Summarize document or chunks using qwen2.5:14b with full context.

- [ ] **Step 3: Implement basic Q&A**

Answer questions using full document text as context (no vector search yet).

- [ ] **Step 4: Test with sample documents**

```bash
# Create sample document
mkdir -p data/raw
echo "# Sample Document\n\nThis is a test document about RAG (Retrieval-Augmented Generation). RAG combines retrieval and generation to provide accurate, context-aware answers." > data/raw/sample_01.md

# Test summarization
uv run python -c "from contentbase.summarization import Summarizer; print(Summarizer().summarize_file('data/raw/sample_01.md'))"

# Test Q&A
uv run python -c "from contentbase.generation import Generator; print(Generator().query('Что такое RAG?', context_file='data/raw/sample_01.md'))"
```

Expected: summaries and answers are generated correctly.

- [ ] **Step 5: Commit**

```bash
git add src/contentbase/generation.py src/contentbase/summarization.py data/raw/sample_01.md
git commit -m "feat: add summarization and basic qa without vector search"
```

### Task 1.5: Add Langfuse tracing (Phase 1)

**Files:**
- Create: src/contentbase/tracing.py
- Modify: src/contentbase/generation.py
- Modify: src/contentbase/summarization.py

- [ ] **Step 1: Implement Langfuse client**

Initialize Langfuse SDK with env vars, add helper methods:
- create_trace()
- create_span()
- log_generation()
- log_score()

- [ ] **Step 2: Instrument summarization**

Trace name: document_summary.
Span: llm_generation.
Log: input_length, output_length, compression_ratio.

- [ ] **Step 3: Instrument basic Q&A**

Trace name: basic_query.
Span: llm_generation.
Log: question, answer, latency_ms.

- [ ] **Step 4: Create .env for testing**

```bash
cp .env.example .env
# Fill in Langfuse keys from http://localhost:3000
```

- [ ] **Step 5: Test tracing**

Run summarization and Q&A, check Langfuse UI.

- [ ] **Step 6: Commit**

```bash
git add src/contentbase/tracing.py src/contentbase/generation.py src/contentbase/summarization.py
git commit -m "feat: add langfuse tracing for summarization and basic qa"
```

### Task 1.6: Implement CLI

**Files:**
- Create: src/contentbase/app.py

- [ ] **Step 1: Implement CLI using Typer**

Commands:
- summarize: summarize a document
- query: answer a question (basic, full context)
- ingest: load and chunk documents

- [ ] **Step 2: Test CLI**

```bash
uv run python -m contentbase.app summarize --input data/raw/sample_01.md
uv run python -m contentbase.app query --question "Что такое RAG?" --input data/raw/sample_01.md
```

Expected: CLI works correctly.

- [ ] **Step 3: Commit**

```bash
git add src/contentbase/app.py
git commit -m "feat: add CLI interface"
```

### Task 1.7: Create Phase 1 demo notebook

**Files:**
- Create: notebooks/01_phase1_basic_processing.ipynb

- [ ] **Step 1: Create demo notebook**

Show:
- Document ingestion
- Summarization of documents
- Q&A with full document context
- Langfuse traces for both operations
- Comparison of summary length vs original

- [ ] **Step 2: Verify Langfuse UI**

Check that traces appear in Langfuse UI at http://localhost:3000.

- [ ] **Step 3: Commit**

```bash
git add notebooks/01_phase1_basic_processing.ipynb
git commit -m "docs: add phase 1 demo notebook"
```

---

## Phase 2 — Vector Database and RAG

**Goal:** Add vector database, embeddings, and semantic search to enable true RAG.

### Task 2.1: Add dependencies for vector database

**Files:**
- Modify: pyproject.toml

- [ ] **Step 1: Add Qdrant client**

```bash
uv add qdrant-client
```

Expected: dependency added.

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add qdrant-client dependency"
```

### Task 2.2: Implement embeddings

**Files:**
- Create: docker-compose.yml
- Create: src/contentbase/embeddings.py

- [ ] **Step 1: Create docker-compose.yml**

Add Qdrant service (no Langfuse yet, optional for Phase 2).

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

volumes:
  qdrant_data:
```

- [ ] **Step 2: Start Qdrant**

On 10.66.66.12:

```bash
cd /path/to/contentbase
docker compose up -d qdrant
```

Expected: Qdrant available at http://localhost:6333.

- [ ] **Step 3: Implement Ollama embeddings client**

Use model from env OLLAMA_EMBEDDING_MODEL=bge-m3.

- [ ] **Step 4: Test embeddings**

```bash
uv run python -c "from contentbase.embeddings import OllamaEmbeddings; e = OllamaEmbeddings(); vec = e.embed('test'); print(f'Dimension: {len(vec)}, Vector: {vec[:5]}...')"
```

Expected: embedding vector is returned (typically 1024 dimensions for bge-m3).

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml src/contentbase/embeddings.py
git commit -m "feat: add ollama embeddings and qdrant docker compose"
```

### Task 2.3: Implement vector store

**Files:**
- Create: src/contentbase/vector_store.py

- [ ] **Step 1: Implement Qdrant collection management**

Create collection with cosine distance, recreate option.

- [ ] **Step 2: Implement upsert**

Upsert chunks with embeddings and metadata.

- [ ] **Step 3: Implement search**

Search by embedding with optional metadata filters (topic, source).

- [ ] **Step 4: Test vector store**

```bash
uv run python -c "
from contentbase.ingestion import DocumentLoader
from contentbase.chunking import Chunker
from contentbase.embeddings import OllamaEmbeddings
from contentbase.vector_store import VectorStore

# Load and chunk
loader = DocumentLoader()
chunker = Chunker()
embedder = OllamaEmbeddings()
store = VectorStore()

docs = loader.load_dir('data/raw')
chunks = []
for doc in docs:
    chunks.extend(chunker.chunk(doc))

# Embed and index
for chunk in chunks:
    chunk.embedding = embedder.embed(chunk.text)

store.upsert(chunks)
print(f'Indexed {len(chunks)} chunks')

# Test search
results = store.search('RAG', top_k=3)
for r in results:
    print(f'Score: {r.score:.3f}, Text: {r.text[:100]}...')
"
```

Expected: chunks indexed, search returns relevant results.

- [ ] **Step 5: Commit**

```bash
git add src/contentbase/vector_store.py
git commit -m "feat: add qdrant vector store"
```

### Task 2.4: Implement retrieval

**Files:**
- Create: src/contentbase/retrieval.py
- Create: tests/test_retrieval.py

- [ ] **Step 1: Write retrieval tests**

Test top-k, score filtering, metadata filters.

- [ ] **Step 2: Implement retrieval orchestration**

Embed query, search Qdrant, return top-k chunks with scores.

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_retrieval.py -v
```

Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add src/contentbase/retrieval.py tests/test_retrieval.py
git commit -m "feat: add retrieval with vector search"
```

### Task 2.5: Update generation for RAG

**Files:**
- Modify: src/contentbase/generation.py

- [ ] **Step 1: Implement RAG prompt builder**

Build prompt with retrieved chunks as context.

- [ ] **Step 2: Update query method**

Replace full-document context with retrieved chunks.

- [ ] **Step 3: Add source citations**

Include chunk references (doc_id, chunk_id) in output.

- [ ] **Step 4: Update CLI**

Add --rag flag to query command.

- [ ] **Step 5: Test RAG**

```bash
uv run python -m contentbase.app query --question "Что такое RAG?" --rag
```

Expected: answer uses retrieved chunks, includes sources.

- [ ] **Step 6: Commit**

```bash
git add src/contentbase/generation.py src/contentbase/app.py
git commit -m "feat: update generation to use vector-based retrieval"
```

### Task 2.6: Update Langfuse tracing for RAG

**Files:**
- Modify: src/contentbase/tracing.py
- Modify: src/contentbase/retrieval.py
- Modify: src/contentbase/generation.py

- [ ] **Step 1: Add RAG query trace**

Trace name: rag_query.
Spans: embed_query, retrieve_context, build_prompt, llm_generation, evaluate_answer.

- [ ] **Step 2: Add retrieval span**

Log search parameters (top_k, filters) and results.

- [ ] **Step 3: Add generation span**

Log input/output tokens if available.

- [ ] **Step 4: Verify in Langfuse UI**

Check RAG traces show all spans and search results.

- [ ] **Step 5: Commit**

```bash
git add src/contentbase/tracing.py src/contentbase/retrieval.py src/contentbase/generation.py
git commit -m "feat: add langfuse tracing for rag pipeline"
```

### Task 2.7: Create Phase 2 demo notebook

**Files:**
- Create: notebooks/02_phase2_rag_demo.ipynb

- [ ] **Step 1: Create demo notebook**

Show:
- Document indexing to Qdrant
- Semantic search for queries
- RAG generation with retrieved context
- Comparison with Phase 1 basic Q&A
- Latency comparison

- [ ] **Step 2: Verify Langfuse UI**

Check that RAG traces show all spans and search results.

- [ ] **Step 3: Commit**

```bash
git add notebooks/02_phase2_rag_demo.ipynb
git commit -m "docs: add phase 2 rag demo notebook"
```

---

## Phase 3 — Evaluation and Homework Report

**Goal:** Implement custom evaluator, create Langfuse dataset/experiment, write final report.

### Task 3.1: Add full Langfuse stack (optional)

**Files:**
- Modify: docker-compose.yml

- [ ] **Step 1: Add Langfuse services**

Add PostgreSQL, ClickHouse, Redis, MinIO to docker-compose.yml (use official Langfuse compose).

- [ ] **Step 2: Start Langfuse**

On 10.66.66.12:

```bash
cd /path/to/contentbase
docker compose up -d
```

Expected: Langfuse UI available at http://localhost:3000.

- [ ] **Step 3: Create project and API keys**

Follow instructions from agentic-rag-workshop README.

- [ ] **Step 4: Update .env**

Add Langfuse keys to .env.

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml
git commit -m "chore: add full langfuse stack to docker compose"
```

### Task 3.2: Implement custom evaluator

**Files:**
- Create: src/contentbase/evaluation.py
- Create: tests/test_evaluation.py

- [ ] **Step 1: Write evaluator tests**

Test citation presence, expected keyword match, empty answer penalty.

- [ ] **Step 2: Implement evaluator**

Return answer_relevance, context_usage, citation_presence, honesty_when_unknown, final_score.

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_evaluation.py -v
```

Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add src/contentbase/evaluation.py tests/test_evaluation.py
git commit -m "feat: add custom evaluator"
```

### Task 3.3: Create Langfuse dataset and experiment

**Files:**
- Create: notebooks/03_langfuse_dataset_experiment.ipynb

- [ ] **Step 1: Create dataset contentbase_rag_eval_v1**

Add at least 10 dataset items with questions and expected outputs.

Example items:
1. "Что такое RAG?"
2. "Какие преимущества у RAG?"
3. "Что такое chunking?"
4. "Как работает эмбеддинг?"
5. "Что такое vector database?"
6. "Какой топ-k используется?"
7. "Как фильтровать по источникам?"
8. "Какой размер чанков?"
9. "Что такое Langfuse?"
10. "Как оценить качество RAG?"

- [ ] **Step 2: Create experiment contentbase_qdrant_top5_baseline**

Define experiment parameters:
- vector_db: qdrant
- embedding_model: bge-m3
- llm_model: qwen2.5:14b
- top_k: 5
- chunk_size: 1200
- chunk_overlap: 200

- [ ] **Step 3: Run experiment**

Execute experiment with RAG pipeline.

- [ ] **Step 4: Review results**

Check experiment runs and scores in Langfuse UI.

- [ ] **Step 5: Commit**

```bash
git add notebooks/03_langfuse_dataset_experiment.ipynb
git commit -m "docs: add langfuse dataset and experiment notebook"
```

### Task 3.4: Add integration tests

**Files:**
- Create: tests/test_integration.py

- [ ] **Step 1: Write end-to-end test**

Test full pipeline: ingest -> chunk -> embed -> index -> retrieve -> generate.

- [ ] **Step 2: Run integration tests**

```bash
uv run pytest tests/test_integration.py -v
```

Expected: pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration test"
```

### Task 3.5: Final report and screenshots

**Files:**
- Create: docs/report.md
- Create: docs/screenshots/*.png

- [ ] **Step 1: Capture screenshots**

Required:
- traces overview
- detailed RAG trace
- observation
- dashboards
- dataset contentbase_rag_eval_v1 (showing 10+ items)
- experiment contentbase_qdrant_top5_baseline
- custom evaluator
- Phase 1 vs Phase 2 comparison

- [ ] **Step 2: Write report**

Include:
- Architecture overview
- Phase 1 implementation
- Phase 2 implementation
- Phase 3 evaluation
- Test queries and results
- Metrics (latency, retrieval quality, token usage)
- Limitations
- Conclusions

- [ ] **Step 3: Update README**

Add links to report and notebooks.

- [ ] **Step 4: Final commit and push**

```bash
git add docs/ README.md
git commit -m "docs: add homework report and langfuse screenshots"
git push
```

---

## Verification Checklist

### Phase 1 (Basic Processing):
- [ ] ollama list shows qwen2.5:14b
- [ ] Documents can be loaded from data/raw/
- [ ] Summarization works for documents
- [ ] Basic Q&A works with full document context
- [ ] Langfuse traces appear for summarization and queries
- [ ] CLI commands work (summarize, query)
- [ ] Demo notebook 01_phase1_basic_processing.ipynb runs end-to-end

### Phase 2 (Vector Database):
- [ ] ollama list shows bge-m3
- [ ] docker compose ps shows Qdrant running
- [ ] Documents can be indexed to Qdrant
- [ ] Semantic search returns relevant chunks
- [ ] RAG generation uses retrieved chunks
- [ ] Source citations appear in answers
- [ ] Langfuse traces show embed_query and retrieve_context spans
- [ ] Demo notebook 02_phase2_rag_demo.ipynb runs end-to-end

### Phase 3 (Evaluation):
- [ ] docker compose ps shows Langfuse services running (if local)
- [ ] uv run pytest passes all tests
- [ ] Dataset contentbase_rag_eval_v1 has at least 10 items
- [ ] Experiment contentbase_qdrant_top5_baseline exists
- [ ] Custom evaluator produces scores
- [ ] All required screenshots are captured
- [ ] Report includes Phase 1 vs Phase 2 comparison
- [ ] GitHub repo has README, notebooks, code, report, screenshots
- [ ] .env is not committed

---

## Self-Review

Spec coverage:
- LLM app: covered by generation/summarization/content generation
- RAG: covered by ingestion/chunking/embeddings/Qdrant/retrieval
- Langfuse: covered by traces/spans/generations/events/scores
- Datasets/experiments: covered by notebook and evaluator (10 items minimum)
- Vector DB analysis: must be documented in docs/report.md with top-k/latency comparison
- Local model: covered by Ollama qwen2.5:14b and bge-m3
- GitHub delivery: covered by repo workflow

Two-phase approach benefits:
1. **Phase 1** validates LLM integration and Langfuse quickly without vector DB complexity
2. **Phase 2** builds on working foundation to add vector search
3. Easier to debug each component separately
4. Can demonstrate evolution from basic Q&A to true RAG

Known gaps to watch:
- Zed may not be ideal for Jupyter notebooks; keep VS Code fallback
- Local Langfuse setup may take time; Langfuse Cloud remains acceptable fallback
- qwen2.5:14b may be slow on CPU; acceptable because quality is prioritized
- Docker Desktop vs Docker Compose on 10.66.66.12 — verify which approach works

---

## Appendix A: Professional README Template

```markdown
# ContentBase

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-0.1.x-purple.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A local-first multi-agent RAG system for building thematic knowledge bases and generating grounded content. Designed for the OTUS "LLM Driven Development" course.

## Features

- 📄 **Document Ingestion**: Load and process `.md` and `.txt` files with automatic metadata extraction
- 🔪 **Smart Chunking**: Overlapping chunks (1200 chars, 200 overlap) optimized for Russian text
- 🔍 **Semantic Search**: Vector-based retrieval with Qdrant and multilingual embeddings
- 🤖 **Local LLM**: Full privacy with Ollama (qwen2.5:14b for generation, bge-m3 for embeddings)
- 📊 **Observability**: Complete Langfuse integration with traces, spans, and scores
- 🧪 **Custom Evaluation**: Customizable evaluator with relevance, context usage, and citation metrics
- 📝 **Multiple Modes**: Summarization, Q&A, and content generation
- 🚀 **CLI Interface**: Command-line tools for all operations
- 📓 **Jupyter Notebooks**: Interactive demos for learning and testing

## Architecture

ContentBase implements a modular RAG pipeline with the following components:

```
User Input (Question/Document)
         ↓
    [Ingestion]
         ↓
    [Chunking]
         ↓
  [Embeddings] → Ollama (bge-m3)
         ↓
   [Vector Store] → Qdrant
         ↓
    [Retrieval]
         ↓
 [RAG Prompt Builder]
         ↓
   [Generation] → Ollama (qwen2.5:14b)
         ↓
   [Answer + Sources]
         ↓
    [Langfuse] ← All operations traced
```

### Phase-based Development

The project is implemented in three phases:

1. **Phase 1**: Basic document processing (summarization, Q&A with full context)
2. **Phase 2**: Vector database and semantic search (true RAG)
3. **Phase 3**: Evaluation and dataset experiments

See the [implementation plan](docs/implementation-plan.md) for details.

## Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Ollama (or use via Docker)
- [uv](https://github.com/astral-sh/uv) package manager

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/your-username/contentbase.git
cd contentbase
```

2. **Install dependencies**

```bash
uv sync
```

3. **Start infrastructure**

```bash
# On development machine (10.66.66.12)
docker compose up -d
```

4. **Pull Ollama models**

```bash
ollama pull qwen2.5:14b
ollama pull bge-m3
```

5. **Configure environment**

```bash
cp .env.example .env
# Edit .env and add your Langfuse API keys
```

6. **Run the application**

```bash
uv run python -m contentbase.app --help
```

## Usage

### Summarize a document

```bash
uv run python -m contentbase.app summarize --input data/raw/document.md
```

### Answer a question (RAG mode)

```bash
uv run python -m contentbase.app query --question "What is RAG?" --rag
```

### Answer a question (basic mode, full context)

```bash
uv run python -m contentbase.app query --question "What is RAG?" --input data/raw/document.md
```

### Ingest documents

```bash
uv run python -m contentbase.app ingest --source data/raw/
```

## Development

### Project Structure

```
contentbase/
├── docs/                 # Documentation
├── data/                 # Source documents
├── notebooks/             # Jupyter notebooks
├── src/contentbase/       # Source code
└── tests/                # Tests
```

### Running tests

```bash
uv run pytest
```

### Code quality

```bash
# Linting
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Jupyter Notebooks

Launch Jupyter:

```bash
uv run jupyter notebook
```

Available notebooks:
- `01_phase1_basic_processing.ipynb` - Basic document processing
- `02_phase2_rag_demo.ipynb` - RAG with vector search
- `03_langfuse_dataset_experiment.ipynb` - Dataset and experiments

## Observability

ContentBase integrates with [Langfuse](https://langfuse.com/) for complete observability:

1. Access Langfuse UI at http://localhost:3000
2. Create a project and get API keys
3. Add keys to `.env`
4. All operations are traced automatically

View traces, spans, and scores in the Langfuse dashboard.

## Evaluation

The project includes a custom evaluator that measures:

- **Answer Relevance**: How well the answer matches the question
- **Context Usage**: Whether retrieved context is actually used
- **Citation Presence**: Whether sources are cited
- **Honesty**: Whether the system admits when it doesn't know

See `notebooks/03_langfuse_dataset_experiment.ipynb` for evaluation examples.

## Tech Stack

- **LLM**: [Ollama](https://ollama.com/) (qwen2.5:14b)
- **Embeddings**: [Ollama](https://ollama.com/) (bge-m3)
- **Vector Database**: [Qdrant](https://qdrant.tech/)
- **Observability**: [Langfuse](https://langfuse.com/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Testing**: [pytest](https://docs.pytest.org/)
- **Type Checking**: [mypy](https://mypy-lang.org/)

## Roadmap

- [ ] Streamlit UI for easier interaction
- [ ] Multi-document summarization
- [ ] PDF ingestion support
- [ ] Advanced retrieval (hybrid search, reranking)
- [ ] LLM-as-a-judge evaluator

## Contributing

This is an educational project for the OTUS course. Feedback and suggestions are welcome!

## License

[MIT](LICENSE) - feel free to use this project for learning and experimentation.

## Acknowledgments

- Inspired by [agentic-rag-workshop](https://github.com/pueraeternis/agentic-rag-workshop)
- OTUS "LLM Driven Development" course
```

---

## Appendix B: Docker Compose for Development

Complete docker-compose.yml for Phase 2+ (including Langfuse):

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  # Langfuse stack (optional, add in Phase 3)
  # See https://github.com/langfuse/langfuse/tree/main/docker-compose for full setup

volumes:
  qdrant_data:
```

For full Langfuse stack, use the official docker-compose from:
https://github.com/langfuse/langfuse/tree/main/docker-compose
