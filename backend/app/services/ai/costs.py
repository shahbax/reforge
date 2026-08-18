"""Token/cost accounting for LLM calls.

Prices are USD per 1M tokens (input, output). These are configurable estimates
used to surface per-project and per-user cost — update them to your provider's
live pricing. Mock calls cost nothing but still record estimated token volume so
the usage UI is exercised end-to-end in development.
"""
from __future__ import annotations

# (input_per_mtok, output_per_mtok) in USD. Estimates — keep in sync with billing.
PRICING: dict[str, tuple[float, float]] = {
    "claude-sonnet-5": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (0.80, 4.00),
    "claude-opus-4-8": (15.00, 75.00),
    "mock": (0.0, 0.0),
}

_DEFAULT_PRICE = (3.00, 15.00)


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token). Real providers report exact usage;
    this is only used when a provider cannot (e.g. the mock provider)."""
    return max(1, len(text) // 4)


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    inp, out = PRICING.get(model, _DEFAULT_PRICE)
    return round(input_tokens / 1_000_000 * inp + output_tokens / 1_000_000 * out, 6)
