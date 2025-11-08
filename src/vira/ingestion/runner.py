"""Command-line utilities wrapping the Scrapy crawler."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from scrapy.crawler import CrawlerProcess

from .crawl_config import CrawlConfig, ensure_directories, load_crawl_config
from .spider import A16ZSpider

app = typer.Typer(add_completion=False, help="Crawl and process a16z content for VIRA.")


def _default_settings(cfg: CrawlConfig) -> dict[str, Any]:
    return {
        "DOWNLOAD_DELAY": cfg.download_delay,
        "CONCURRENT_REQUESTS": cfg.concurrent_requests,
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            str(cfg.output_dir / "a16z_raw.jsonl"): {
                "format": "jsonlines",
                "encoding": "utf-8",
                "overwrite": True,
            }
        },
        "USER_AGENT": cfg.user_agent,
    }


@app.command()
def crawl(config_path: Path = typer.Option(..., exists=True, dir_okay=False, resolve_path=True)) -> None:
    """Run the Scrapy crawler using the supplied YAML config."""

    cfg = load_crawl_config(config_path)
    ensure_directories([cfg.output_dir, cfg.processed_dir])

    process = CrawlerProcess(_default_settings(cfg))
    process.crawl(A16ZSpider, cfg=cfg, output_path=cfg.output_dir)
    process.start()


def main() -> None:
    app()


if __name__ == "__main__":
    main()

