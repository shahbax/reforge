"""LLM provider abstraction.

`complete()` returns schema-validated JSON; `embed()` returns vectors.
- ClaudeProvider: production integration (Anthropic Messages API).
- MockProvider: schema-valid fixtures so the whole pipeline + UI run with no keys
  (development fallback only — production must configure a real provider).

Selection is driven by config; a missing key transparently falls back to Mock in
development so the app is always runnable.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

from app.config import get_settings
from app.services.ai import costs

log = logging.getLogger("reforge.ai")
T = TypeVar("T", bound=BaseModel)


class AIError(RuntimeError):
    pass


class BaseProvider:
    def __init__(self) -> None:
        # Per-instance ledger of every LLM call, consumed by usage accounting.
        self.usage: list[dict] = []

    def complete(self, *, system: str, user: str, schema: Type[T], tier: str = "strong") -> T:
        raise NotImplementedError

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def _record(self, stage: str, model: str, input_tokens: int, output_tokens: int) -> None:
        self.usage.append(
            {
                "stage": stage,
                "model": model,
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "cost_usd": costs.cost_usd(model, int(input_tokens), int(output_tokens)),
            }
        )


# --------------------------------------------------------------------------- #
# Claude (production)
# --------------------------------------------------------------------------- #
class ClaudeProvider(BaseProvider):
    def __init__(self) -> None:
        from anthropic import Anthropic  # imported lazily so mock runs without the dep

        super().__init__()
        s = get_settings()
        if not s.anthropic_api_key:
            raise AIError("ANTHROPIC_API_KEY missing")
        self._client = Anthropic(api_key=s.anthropic_api_key)
        self._model = {"strong": s.model_strong, "cheap": s.model_cheap}

    def complete(self, *, system: str, user: str, schema: Type[T], tier: str = "strong") -> T:
        model = self._model.get(tier, self._model["strong"])
        instruction = (
            f"{user}\n\nReturn ONLY valid minified JSON matching this schema, no prose:\n"
            f"{json.dumps(schema.model_json_schema())}"
        )
        raw = self._call(system, instruction, model, schema.__name__)
        try:
            return schema.model_validate_json(_extract_json(raw))
        except ValidationError:
            # one repair attempt
            repair = f"Your previous output failed validation. Fix it. Errors matter. Original:\n{raw}"
            raw2 = self._call(system, repair + "\n\n" + instruction, model, schema.__name__)
            return schema.model_validate_json(_extract_json(raw2))

    def _call(self, system: str, user: str, model: str, stage: str) -> str:
        from anthropic import APIError

        try:
            msg = self._client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except APIError as e:  # pragma: no cover - network
            raise AIError(f"Anthropic API error: {e}") from e
        text = "".join(block.text for block in msg.content if block.type == "text")
        u = getattr(msg, "usage", None)
        self._record(
            stage,
            model,
            getattr(u, "input_tokens", None) or costs.estimate_tokens(system + user),
            getattr(u, "output_tokens", None) or costs.estimate_tokens(text),
        )
        return text

    def embed(self, texts: list[str]) -> list[list[float]]:
        # Anthropic has no first-party embeddings endpoint; use OpenAI or a local
        # model in production. Fall back to the deterministic hash embedding so the
        # originality guard still functions if embeddings aren't configured.
        return _hash_embeddings(texts)


# --------------------------------------------------------------------------- #
# Mock (development fallback / tests)
# --------------------------------------------------------------------------- #
class MockProvider(BaseProvider):
    """Returns deterministic, schema-valid fixtures keyed by the target schema."""

    def complete(self, *, system: str, user: str, schema: Type[T], tier: str = "strong") -> T:
        from app.services.ai.fixtures import fixture_for

        data = fixture_for(schema.__name__, user)
        result = schema.model_validate(data)
        # Record estimated volume so usage accounting is exercised in dev/tests.
        self._record(
            schema.__name__,
            "mock",
            costs.estimate_tokens(system + user),
            costs.estimate_tokens(result.model_dump_json()),
        )
        return result

    def embed(self, texts: list[str]) -> list[list[float]]:
        return _hash_embeddings(texts)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _extract_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start : end + 1]
    return raw


def _hash_embeddings(texts: list[str], dims: int = 256) -> list[list[float]]:
    """Deterministic bag-of-words hashing embedding.

    Not semantically perfect, but real and dependency-free: it gives the
    originality guard a functioning semantic-similarity signal offline and in
    tests. Production ClaudeProvider can be pointed at a real embedding model.
    """
    out: list[list[float]] = []
    for text in texts:
        vec = [0.0] * dims
        for token in _tokens(text):
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % dims] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        out.append([v / norm for v in vec])
    return out


def _tokens(text: str) -> list[str]:
    return [t for t in "".join(c.lower() if c.isalnum() else " " for c in text).split() if t]


def get_provider() -> BaseProvider:
    s = get_settings()
    if s.use_mock_ai:
        log.info("Using MockProvider (no API key configured / provider=mock)")
        return MockProvider()
    if s.ai_provider == "claude":
        return ClaudeProvider()
    raise AIError(f"Unsupported ai_provider: {s.ai_provider}")
