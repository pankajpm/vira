"""Scrapy spider implementation for harvesting a16z content."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import scrapy
from scrapy.http import Response

from .crawl_config import CrawlConfig


class A16ZSpider(scrapy.Spider):
    """Scrapy spider tailored to crawl the curated a16z properties.

    The spider only follows links that stay within the allowed_domains and
    respects a configurable exclusion list (e.g., pagination search URLs).
    Parsed bodies are stored as JSON lines by the runner (see `runner.py`).
    """

    name = "a16z"

    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS": 2,
        "FEED_FORMAT": "jsonlines",
    }

    def __init__(self, cfg: CrawlConfig, output_path: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cfg = cfg
        self.output_path = output_path
        self.start_urls = cfg.seed_urls
        self.allowed_domains = cfg.allowed_domains
        self.page_count = 0

    def parse(self, response: Response, **kwargs):  # type: ignore[override]
        """Extract page metadata and yield follow-up requests."""

        if self.cfg.should_exclude(response.url):
            return

        self.page_count += 1
        yield self._build_record(response)

        if self.page_count >= self.cfg.max_pages:
            return

        for href in self._iter_valid_links(response):
            yield response.follow(href, callback=self.parse)

    def _iter_valid_links(self, response: Response) -> Iterable[str]:
        for href in response.css("a::attr(href)").getall():
            if not href:
                continue
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            if href.startswith("javascript:") or href.startswith("tel:"):
                continue
            absolute = response.urljoin(href)
            if self.cfg.should_exclude(absolute):
                continue
            yield absolute

    def _build_record(self, response: Response) -> dict:
        body = "\n".join(
            part.strip()
            for part in response.css("article, main, body").xpath("string() ").getall()
            if part.strip()
        )

        flat_metadata = {
            "url": response.url,
            "status": response.status,
            "scraped_at": datetime.utcnow().isoformat(),
            "title": response.css("title::text").get(default="").strip(),
            "content_type": response.headers.get("Content-Type", b"").decode("utf-8", "ignore"),
        }

        if self.cfg.metadata:
            flat_metadata.update({f"meta_{key}": value for key, value in self.cfg.metadata.items()})

        return {
            "url": response.url,
            "status": response.status,
            "scraped_at": datetime.utcnow().isoformat(),
            "title": response.css("title::text").get(default="").strip(),
            "content": body,
            "metadata": flat_metadata,
        }


__all__ = ["A16ZSpider"]

