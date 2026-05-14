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
    user_id: str = typer.Option("demo-user", "--user-id", help="Langfuse user id"),
    session_id: str = typer.Option("contentbase-demo", "--session-id", help="Langfuse session id"),
):
    """Загрузить и разбить на чанки документы из исходной директории.

    Читает документы из указанной директории, извлекает метаданные
    и разбивает текст на чанки.
    """
    console.print(f"[bold blue]Ingesting documents from[/bold blue] {source}")
    console.print()

    tracing = get_tracing_client()
    with tracing.trace(
        "document_ingestion",
        input_data={"source": source},
        user_id=user_id,
        session_id=session_id,
        tags=["contentbase", "ingestion"],
        metadata={"source": source, "command": "ingest"},
    ):
        tracing.log_event("ingest_started", metadata={"source": source})

        # Загружаем документы.
        loader = DocumentLoader()
        with tracing.span("load_documents", input_data={"source": source}):
            documents = loader.load_dir(source)
            tracing.update_current_span(
                output={"document_count": len(documents)},
                metadata={"doc_ids": [doc.doc_id for doc in documents]},
            )

        if not documents:
            tracing.log_event("ingest_failed", metadata={"reason": "no_documents"}, level="WARNING")
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
        with tracing.span(
            "chunk_documents",
            input_data={"document_count": len(documents)},
            metadata={
                "chunk_size_chars": chunker.chunk_size_chars,
                "chunk_overlap_chars": chunker.chunk_overlap_chars,
            },
        ):
            chunks = chunker.chunk_documents(documents)
            tracing.update_current_span(
                output={"chunk_count": len(chunks)},
                metadata={"chunk_ids": [chunk.chunk_id for chunk in chunks[:20]]},
            )

        tracing.set_current_trace_io(
            input_data={"source": source},
            output_data={
                "document_count": len(documents),
                "chunk_count": len(chunks),
            },
        )
        tracing.log_event(
            "ingest_completed",
            metadata={"document_count": len(documents), "chunk_count": len(chunks)},
        )

        console.print(f"[bold green]Ingestion complete:[/bold green] {len(documents)} documents → {len(chunks)} chunks")
        console.print("[dim]Use 'summarize' or 'query' to work with documents[/dim]")


@app.command()
def summarize(
    input: str = typer.Argument(..., help="Path to document file"),
    max_length: int = typer.Option(300, "--max-length", "-m", help="Maximum summary length"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    user_id: str = typer.Option("demo-user", "--user-id", help="Langfuse user id"),
    session_id: str = typer.Option("contentbase-demo", "--session-id", help="Langfuse session id"),
):
    """Сделать краткий пересказ документа.

    Саммаризирует указанный документ с помощью локальной LLM.
    """
    console.print(f"[bold blue]Summarizing document:[/bold blue] {input}")
    console.print()

    tracing = get_tracing_client()
    with tracing.trace(
        "document_summary",
        input_data={"input_file": input, "max_length": max_length},
        user_id=user_id,
        session_id=session_id,
        tags=["contentbase", "summary"],
        metadata={"input_file": input, "max_length": max_length, "command": "summarize"},
    ):
        # Инициализируем компоненты.
        summarizer = Summarizer()

        try:
            tracing.log_event("summary_started", metadata={"input_file": input})

            # Делаем summary.
            result = summarizer.summarize_file(input)

            tracing.set_current_trace_io(
                input_data={"input_file": input, "max_length": max_length},
                output_data={"summary": result["summary"]},
            )
            tracing.log_score(
                "compression_ratio",
                float(result["compression_ratio"]),
                comment="Output length divided by input length",
            )
            tracing.log_event(
                "summary_completed",
                metadata={
                    "input_length": result["input_length"],
                    "output_length": result["output_length"],
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
            tracing.log_event("summary_error", metadata={"error": str(e)}, level="ERROR")
            raise typer.Exit(1)


@app.command()
def query(
    question: str = typer.Option(..., "--question", "-q", help="Question to answer"),
    input: str = typer.Option(None, "--input", "-i", help="Path to context file or directory (basic Q&A mode)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    user_id: str = typer.Option("demo-user", "--user-id", help="Langfuse user id"),
    session_id: str = typer.Option("contentbase-demo", "--session-id", help="Langfuse session id"),
    evaluate: bool = typer.Option(True, "--evaluate/--no-evaluate", help="Run custom evaluator and write scores"),
    llm_judge: bool = typer.Option(False, "--llm-judge", help="Run LLM-as-a-judge and write score"),
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

    tracing = get_tracing_client()
    with tracing.trace(
        "basic_query" if input else "pure_generation",
        input_data={"question": question, "context_file": input},
        user_id=user_id,
        session_id=session_id,
        tags=["contentbase", "qa", mode],
        metadata={
            "mode": mode,
            "context_file": input,
            "command": "query",
            "evaluate": evaluate,
            "llm_judge": llm_judge,
        },
    ):
        # Инициализируем компоненты.
        generator = Generator()

        try:
            tracing.log_event("query_started", metadata={"mode": mode})

            # Генерируем ответ.
            result = generator.answer_question(
                question=question,
                context=None,  # В Phase 1 RAG ещё не подключён.
                context_file=input,
                evaluate=evaluate,
                llm_judge=llm_judge,
            )
            tracing.set_current_trace_io(
                input_data={"question": question, "context_file": input},
                output_data={"answer": result.answer, "sources": result.sources},
            )
            tracing.log_event(
                "query_completed",
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
            tracing.log_event("qa_error", metadata={"error": str(e)}, level="ERROR")
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
