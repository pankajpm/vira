"""LangSmith integration utilities."""

from __future__ import annotations

import os
from typing import Any


def init_langsmith() -> bool:
    """Initialize LangSmith tracing.

    Returns:
        True if initialized successfully
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    project = os.getenv("LANGSMITH_PROJECT", "vira-alignment")

    if not api_key:
        return False

    try:
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = project
        os.environ["LANGCHAIN_API_KEY"] = api_key
        return True
    except Exception:
        return False


def get_langsmith_trace_url(run_id: str | None = None) -> str | None:
    """Get LangSmith trace URL for a run.

    Args:
        run_id: LangChain run ID

    Returns:
        Trace URL or None if not available
    """
    if not run_id:
        return None

    project = os.getenv("LANGSMITH_PROJECT", "vira-alignment")
    base_url = "https://smith.langchain.com"

    return f"{base_url}/o/project/{project}/r/{run_id}"


def is_langsmith_enabled() -> bool:
    """Check if LangSmith is configured.

    Returns:
        True if enabled
    """
    return bool(os.getenv("LANGSMITH_API_KEY"))


def get_trace_metadata() -> dict[str, Any]:
    """Get metadata for LangSmith tracing.

    Returns:
        Metadata dictionary
    """
    return {
        "project": os.getenv("LANGSMITH_PROJECT", "vira-alignment"),
        "enabled": is_langsmith_enabled(),
    }

