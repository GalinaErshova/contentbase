"""CLI-приложение ContentBase.

Командный интерфейс для обработки документов, Q&A и саммаризации.
"""
import typer
from rich.console import Console
from rich.table import Table

from contentbase.config import get_settings
from contentbase.ingestion import DocumentLoader
from contentbase.chunking import Chunker
from contentbase.generation import Generator
from contentbase.summarization import Summarizer
from contentbase.tracing import get_tracing_client

app = typer.Typer(
    name="contentbase",
    help="ContentBase: Local-first multi-agent RAG system",
    no_args_is_help=True,
)
console = Console()


@app.command()
def ingest(
    source: str = typer.Argument(..., help="Path to source directory (e.g., data/raw)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Загрузить и разбить на чанки документы из исходной директории.

    Читает документы из указанной директории, извлекает метаданные
    и разбивает текст на чанки.
    """
    console.print(f"[bold blue]Ingesting documents from[/bold blue] {source}")
    console.print()

    # Загружаем документы.
    loader = DocumentLoader()
    documents = loader.load_dir(source)

    if not documents:
        console.print("[red]No documents found[/red]")
        raise typer.Exit(1)

    # Показываем загруженные документы.
    if verbose:
        table = Table(title="Loaded Documents")
        table.add_column("doc_id")
        table.add_column("title")
        table.add_column("topic")
        table.add_column("language")

        for doc in documents:
            table.add_row(doc.doc_id, doc.title, doc.topic, doc.language)

        console.print(table)

    # Разбиваем документы на чанки.
    chunker = Chunker()
    chunks = chunker.chunk_documents(documents)

    console.print(f"[bold green]Ingestion complete:[/bold green] {len(documents)} documents → {len(chunks)} chunks")
    console.print("[dim]Use 'summarize' or 'query' to work with documents[/dim]")


@app.command()
def summarize(
    input: str = typer.Argument(..., help="Path to document file"),
    max_length: int = typer.Option(300, "--max-length", "-m", help="Maximum summary length"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Сделать краткий пересказ документа.

    Саммаризирует указанный документ с помощью локальной LLM.
    """
    console.print(f"[bold blue]Summarizing document:[/bold blue] {input}")
    console.print()

    # Инициализируем компоненты.
    summarizer = Summarizer()
    tracing = get_tracing_client()

    # Создаём trace.
    trace = None
    if tracing.is_enabled():
        trace = tracing.create_trace(
            name="document_summary",
            metadata={"input_file": input, "max_length": max_length},
        )

    try:
        # Делаем summary.
        result = summarizer.summarize_file(input)

        # Логируем генерацию.
        if trace:
            tracing.log_generation(
                trace=trace,
                name="summary_generation",
                model=get_settings().ollama_chat_model,
                input_text=f"Document: {result['title']}, length: {result['input_length']}",
                output_text=result["summary"],
                metadata={
                    "input_length": result["input_length"],
                    "output_length": result["output_length"],
                    "compression_ratio": result["compression_ratio"],
                },
            )

        # Показываем результат.
        if verbose:
            console.print(f"[bold]Title:[/bold] {result['title']}")
            console.print(f"[dim]Input length:[/dim] {result['input_length']} chars")
            console.print(f"[dim]Output length:[/dim] {result['output_length']} chars")
            console.print(f"[dim]Compression ratio:[/dim] {result['compression_ratio']:.2%}")
            console.print()

        console.print("[bold green]Summary:[/bold green]")
        console.print(result["summary"])

    except Exception as e:
        console.print(f"[red]Error summarizing document:[/red] {e}")
        if trace:
            tracing.log_event(trace, name="summary_error", metadata={"error": str(e)})
        raise typer.Exit(1)


@app.command()
def query(
    question: str = typer.Option(..., "--question", "-q", help="Question to answer"),
    input: str = typer.Option(None, "--input", "-i", help="Path to context file or directory (basic Q&A mode)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Ответить на вопрос.

    В basic-режиме отвечает с использованием полного файла или директории.
    В RAG-режиме (Phase 2) будет отвечать по найденным чанкам.
    """
    console.print(f"[bold blue]Question:[/bold blue] {question}")
    console.print()

    if input:
        console.print("[dim]Mode: Basic Q&A (full file/directory context)[/dim]")
        mode = "basic"
    else:
        console.print("[dim]Mode: Pure generation (no context)[/dim]")
        mode = "pure"

    console.print()

    # Инициализируем компоненты.
    generator = Generator()
    tracing = get_tracing_client()

    # Создаём trace.
    trace = None
    if tracing.is_enabled():
        trace = tracing.create_trace(
            name="basic_query" if input else "pure_generation",
            metadata={
                "mode": mode,
                "context_file": input,
            },
        )

    try:
        # Генерируем ответ.
        result = generator.answer_question(
            question=question,
            context=None,  # В Phase 1 RAG ещё не подключён.
            context_file=input,
        )

        # Логируем генерацию.
        if trace:
            tracing.log_generation(
                trace=trace,
                name="qa_generation",
                model=get_settings().ollama_chat_model,
                input_text=question,
                output_text=result.answer,
                metadata={
                    "mode": mode,
                    "sources": result.sources,
                    "confidence": result.confidence,
                },
            )

        # Показываем результат.
        if verbose:
            console.print(f"[dim]Sources:[/dim] {', '.join(result.sources) if result.sources else 'None'}")
            console.print(f"[dim]Confidence:[/dim] {result.confidence:.2f}")
            console.print()

        console.print("[bold green]Answer:[/bold green]")
        console.print(result.answer)

    except Exception as e:
        console.print(f"[red]Error generating answer:[/red] {e}")
        if trace:
            tracing.log_event(trace, name="qa_error", metadata={"error": str(e)})
        raise typer.Exit(1)


@app.command()
def status():
    """Показать статус ContentBase."""
    settings = get_settings()

    console.print("[bold blue]ContentBase Status[/bold blue]")
    console.print()

    # Статус Ollama.
    console.print("[bold]Ollama Configuration:[/bold]")
    console.print(f"  Base URL: {settings.ollama_base_url}")
    console.print(f"  Chat Model: {settings.ollama_chat_model}")
    console.print(f"  Embedding Model: {settings.ollama_embedding_model}")
    console.print()

    # Статус Qdrant (Phase 2).
    console.print("[bold]Qdrant Configuration (Phase 2):[/bold]")
    console.print(f"  URL: {settings.qdrant_url}")
    console.print(f"  Collection: {settings.qdrant_collection_name}")
    console.print()

    # Статус Langfuse.
    console.print("[bold]Langfuse Configuration:[/bold]")
    if settings.langfuse_public_key:
        console.print(f"  Host: {settings.langfuse_host}")
        console.print("  [green]Configured ✓[/green]")
    else:
        console.print("  [yellow]Not configured - add keys to .env[/yellow]")
    console.print()

    # Настройки приложения.
    console.print("[bold]Application Settings:[/bold]")
    console.print(f"  Default Language: {settings.default_language}")
    console.print(f"  Log Level: {settings.log_level}")


if __name__ == "__main__":
    app()
