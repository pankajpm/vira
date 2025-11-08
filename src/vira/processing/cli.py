"""CLI for transforming crawl output into vector store entries."""

from __future__ import annotations

from pathlib import Path

import typer

from .pipeline import ingest_from_path

app = typer.Typer(add_completion=False, help="Process crawled data and load into Chroma.")


@app.command()
def ingest(raw_path: Path = typer.Option(..., exists=True, dir_okay=False, resolve_path=True)) -> None:
    """Ingest a JSONL file emitted by the crawler into the vector store."""

    total = ingest_from_path(raw_path)
    typer.secho(f"Loaded {total} documents into the vector store.", fg=typer.colors.GREEN)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

