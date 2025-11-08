"""Token counting utilities."""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses a simple heuristic: ~4 characters per token.
    For production, use tiktoken library.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return len(text) // 4


def estimate_tokens_accurate(text: str, model: str = "gpt-4o-mini") -> int:
    """Accurately count tokens using tiktoken.

    Args:
        text: Input text
        model: Model name

    Returns:
        Exact token count
    """
    try:
        import tiktoken

        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except ImportError:
        # Fallback to estimation if tiktoken not available
        return estimate_tokens(text)


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o-mini"
) -> float:
    """Calculate cost for API call.

    Args:
        input_tokens: Input token count
        output_tokens: Output token count
        model: Model name

    Returns:
        Cost in USD
    """
    # Pricing as of 2025 (per 1M tokens)
    pricing = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    rates = pricing.get(model, pricing["gpt-4o-mini"])
    input_cost = (input_tokens / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]

    return input_cost + output_cost

