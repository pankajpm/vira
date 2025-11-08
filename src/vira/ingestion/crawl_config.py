"""Configuration helpers for the a16z content crawler."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

import yaml


@dataclass(slots=True)
class CrawlConfig:
    """Typed representation of crawler configuration."""

    seed_urls: List[str]
    allowed_domains: List[str]
    exclusion_patterns: List[str] = field(default_factory=list)
    max_pages: int = 400
    download_delay: float = 1.0
    concurrent_requests: int = 2
    user_agent: str = "VIRAPrototypeBot/0.1"
    output_dir: Path = Path("./data/raw")
    processed_dir: Path = Path("./data/processed")
    metadata: dict[str, str] = field(default_factory=dict)

    def should_exclude(self, url: str) -> bool:
        """Return True if the url matches any exclusion pattern."""

        return any(pattern in url for pattern in self.exclusion_patterns)


def load_crawl_config(path: Path) -> CrawlConfig:
    """Load crawl settings from a YAML file."""

    with path.open("r", encoding="utf-8") as handle:
        raw_cfg = yaml.safe_load(handle)

    return CrawlConfig(
        seed_urls=list(raw_cfg.get("seed_urls", [])),
        allowed_domains=list(raw_cfg.get("allowed_domains", [])),
        exclusion_patterns=list(raw_cfg.get("exclusion_patterns", [])),
        max_pages=int(raw_cfg.get("max_pages", 400)),
        download_delay=float(raw_cfg.get("download_delay", 1.0)),
        concurrent_requests=int(raw_cfg.get("concurrent_requests", 2)),
        user_agent=str(raw_cfg.get("user_agent", "VIRAPrototypeBot/0.1")),
        output_dir=Path(raw_cfg.get("output_dir", "./data/raw")),
        processed_dir=Path(raw_cfg.get("processed_dir", "./data/processed")),
        metadata=dict(raw_cfg.get("metadata", {})),
    )


def ensure_directories(paths: Iterable[Path]) -> None:
    """Ensure each path exists before the crawler runs."""

    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


__all__ = ["CrawlConfig", "load_crawl_config", "ensure_directories"]

