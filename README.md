# ContentBase

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-0.1.x-purple.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OTUS LLM Driven Development](https://img.shields.io/badge/OTUS-LLM%20Driven%20Development-green.svg)](https://otus.ru/lessons/llm-driven-development)

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

3. **Start infrastructure** (on development machine)

```bash
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
# Edit .env and add your Langfuse API keys from http://localhost:3000
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
│   ├── architecture.md           # Architecture details
│   ├── report.md                # Homework report
│   ├── setup_windows.md         # Windows setup guide
│   └── screenshots/            # Langfuse screenshots
├── data/                 # Source documents
│   └── raw/                   # .md and .txt files
├── notebooks/             # Jupyter notebooks
│   ├── 01_phase1_basic_processing.ipynb
│   ├── 02_phase2_rag_demo.ipynb
│   └── 03_langfuse_dataset_experiment.ipynb
├── src/contentbase/       # Source code
│   ├── config.py              # Configuration loader
│   ├── schemas.py            # Data models
│   ├── ingestion.py           # Document loading
│   ├── chunking.py          # Chunk splitter
│   ├── embeddings.py         # Ollama embeddings
│   ├── vector_store.py       # Qdrant operations
│   ├── retrieval.py          # Search orchestration
│   ├── generation.py         # RAG generation
│   ├── summarization.py      # Summary pipeline
│   ├── evaluation.py         # Custom evaluator
│   ├── tracing.py           # Langfuse wrappers
│   └── app.py              # CLI entry point
└── tests/                # Tests
    ├── test_chunking.py
    ├── test_evaluation.py
    ├── test_retrieval.py
    └── test_integration.py
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
- `01_phase1_basic_processing.ipynb` - Basic document processing (summarization, Q&A)
- `02_phase2_rag_demo.ipynb` - RAG with vector search
- `03_langfuse_dataset_experiment.ipynb` - Dataset creation and experiments

## Observability

ContentBase integrates with [Langfuse](https://langfuse.com/) for complete observability:

1. Access Langfuse UI at http://localhost:3000
2. Create a project and get API keys
3. Add keys to `.env`
4. All operations are traced automatically

View traces, spans, and scores in the Langfuse dashboard.

### Trace Structure

Each RAG query produces a trace with the following spans:

- `embed_query` - Generate embedding for user question
- `retrieve_context` - Search Qdrant for relevant chunks
- `build_prompt` - Construct RAG prompt with retrieved context
- `llm_generation` - Generate answer using LLM
- `evaluate_answer` - Evaluate answer quality

## Evaluation

The project includes a custom evaluator that measures:

- **Answer Relevance** (0-1): How well the answer matches the question
- **Context Usage** (0-1): Whether retrieved context is actually used
- **Citation Presence** (0-1): Whether sources are cited in the answer
- **Honesty** (0-1): Whether the system admits when it doesn't know
- **Final Score** (0-1): Weighted combination of all metrics

Final score formula:
```
final_score = 0.4 * answer_relevance + 
             0.3 * context_usage + 
             0.2 * citation_presence + 
             0.1 * honesty
```

See `notebooks/03_langfuse_dataset_experiment.ipynb` for evaluation examples.

### Dataset

The project includes a Langfuse dataset `contentbase_rag_eval_v1` with 10+ test questions covering:

- RAG concepts
- Chunking and embeddings
- Vector database usage
- Langfuse observability
- Evaluation metrics

### Experiment

Baseline experiment `contentbase_qdrant_top5_baseline` demonstrates:

- top_k = 5
- chunk_size = 1200
- chunk_overlap = 200
- cosine distance

## Tech Stack

| Component | Technology | Purpose |
|-----------|-------------|-----------|
| **LLM** | [Ollama](https://ollama.com/) (qwen2.5:14b) | Text generation |
| **Embeddings** | [Ollama](https://ollama.com/) (bge-m3) | Vector generation |
| **Vector Database** | [Qdrant](https://qdrant.tech/) | Semantic search |
| **Observability** | [Langfuse](https://langfuse.com/) | Tracing & evaluation |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) | Dependency management |
| **Testing** | [pytest](https://docs.pytest.org/) | Unit & integration tests |
| **Type Checking** | [mypy](https://mypy-lang.org/) | Static type checking |
| **Linting** | [ruff](https://github.com/astral-sh/ruff) | Code quality |

## Performance

Target performance metrics:

- **Retrieval latency**: < 500ms for top_k=5
- **Generation latency**: < 30s for summarization
- **End-to-end RAG**: < 10s for typical queries

*Note: Performance depends on hardware. Local LLM inference may be slower on CPU.*

## Roadmap

- [ ] Streamlit UI for easier interaction
- [ ] Multi-document summarization
- [ ] PDF ingestion support
- [ ] Advanced retrieval (hybrid search, reranking)
- [ ] LLM-as-a-judge evaluator
- [ ] Export to Obsidian/Markdown

## Contributing

This is an educational project for the OTUS course. Feedback and suggestions are welcome!

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## License

[MIT](LICENSE) - feel free to use this project for learning and experimentation.

## Acknowledgments

- Inspired by [agentic-rag-workshop](https://github.com/pueraeternis/agentic-rag-workshop)
- OTUS "LLM Driven Development" course
- [Ollama](https://ollama.com/) for local LLM inference
- [Qdrant](https://qdrant.tech/) for vector database
- [Langfuse](https://langfuse.com/) for observability

## Contact

For questions about the course or this project, please use the OTUS course channels.
