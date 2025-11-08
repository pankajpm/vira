"""Centralised runtime configuration for the VIRA prototype.

The module exposes a `Settings` object built with Pydantic so the rest of the
codebase can rely on typed configuration values. Environment variables defined
in `config/env.template` (copy to `.env`) override sensible defaults.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=Path(".env"), env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    serper_api_key: str | None = Field(default=None, alias="SERPER_API_KEY")
    langchain_api_key: str | None = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_endpoint: AnyHttpUrl | None = Field(default=None, alias="LANGCHAIN_ENDPOINT")
    langchain_project: str | None = Field(default=None, alias="LANGCHAIN_PROJECT")

    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    vector_db_dir: Path = Field(default=Path("./data/processed/chroma"), alias="VECTOR_DB_DIR")

    crawl_max_pages: int = Field(default=400, alias="CRAWL_MAX_PAGES")
    crawl_download_delay: float = Field(default=1.0, alias="CRAWL_DOWNLOAD_DELAY")
    crawl_concurrent_requests: int = Field(default=2, alias="CRAWL_CONCURRENT_REQUESTS")
    crawl_storage_dir: Path = Field(default=Path("./data/raw"), alias="CRAWL_STORAGE_DIR")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    streamlit_backend_url: AnyHttpUrl | None = Field(default=None, alias="STREAMLIT_BACKEND_URL")

    crawl_seed_urls: List[AnyHttpUrl] = Field(default_factory=list, alias="CRAWL_SEED_URLS")
    crawl_allowed_domains: List[str] = Field(default_factory=lambda: ["a16z.com"], alias="CRAWL_ALLOWED_DOMAINS")

    # Iteration 2: Reflection Agent Configuration
    enable_reflection: bool = Field(default=False, alias="ENABLE_REFLECTION")
    reflection_confidence_threshold: float = Field(default=0.7, alias="REFLECTION_CONFIDENCE_THRESHOLD")
    max_research_queries: int = Field(default=5, alias="MAX_RESEARCH_QUERIES")
    max_reflection_iterations: int = Field(default=2, alias="MAX_REFLECTION_ITERATIONS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance for reuse across the app."""

    settings = Settings()
    vector_dir = settings.vector_db_dir
    vector_dir.mkdir(parents=True, exist_ok=True)
    settings.crawl_storage_dir.mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "get_settings"]

