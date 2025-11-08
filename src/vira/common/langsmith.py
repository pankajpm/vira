"""Helpers for configuring LangSmith tracing when credentials are available."""

from __future__ import annotations

import os

from ..config.settings import get_settings


def configure_langsmith() -> None:
    """Populate LangSmith environment variables if credentials are provided."""

    settings = get_settings()
    if settings.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
    if settings.langchain_endpoint:
        os.environ.setdefault("LANGCHAIN_ENDPOINT", str(settings.langchain_endpoint))
    if settings.langchain_project:
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")


__all__ = ["configure_langsmith"]

