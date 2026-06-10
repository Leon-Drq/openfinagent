"""
finagent.runtime.llm
====================

A small wrapper around the OpenAI Python SDK that:

* Defaults to ``gpt-4o-mini`` (cheap, decent at structured tasks).
* Picks up ``OPENAI_BASE_URL`` automatically — set it to the Vercel AI
  Gateway, an Azure deployment, or a local llama.cpp server with no
  code changes.
* Returns both the response text and a rough cost estimate so the
  Runner can attribute spend in the audit log.

This is intentionally not a multi-provider abstraction: keep the surface
tiny in v0.x; users who need Anthropic / local models can pass
``OPENAI_BASE_URL`` of an OpenAI-compatible gateway.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Lazy import: keep import-time light and yield a clear error message.
try:
    from openai import AsyncOpenAI  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore[assignment]


# Rough USD-per-1M-token pricing for cost attribution.  These are
# *estimates* used only for the audit log — the runtime never bills.
_PRICING_USD_PER_1M = {
    "gpt-4o-mini":     {"input": 0.15,  "output": 0.60},
    "gpt-4o":          {"input": 2.50,  "output": 10.00},
    "gpt-4.1-mini":    {"input": 0.40,  "output": 1.60},
    "gpt-4.1":         {"input": 2.00,  "output": 8.00},
}


@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float


class LLMClient:
    """Thin async wrapper for OpenAI-compatible chat completions."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
    ) -> None:
        if AsyncOpenAI is None:
            raise RuntimeError(
                "LLMClient requires the 'openai' package. "
                "Install it with: pip install openai"
            )
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        if not self._api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Set it in your environment or "
                ".env file. (For Vercel AI Gateway, set OPENAI_BASE_URL "
                "and use AI_GATEWAY_API_KEY as OPENAI_API_KEY.)"
            )
        self._client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )
        self._default_model = default_model

    async def complete(
        self,
        *,
        system: str,
        user: str,
        model: str | None = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> LLMResponse:
        model_name = model or self._default_model

        response = await self._client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        text = choice.message.content or ""
        usage = response.usage
        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0

        cost = _estimate_cost(model_name, prompt_tokens, completion_tokens)

        return LLMResponse(
            text=text,
            model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
        )


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost using the static pricing table."""

    pricing = _PRICING_USD_PER_1M.get(model)
    if pricing is None:
        # Unknown model: don't lie in the audit log.
        return 0.0
    in_cost = pricing["input"] * prompt_tokens / 1_000_000
    out_cost = pricing["output"] * completion_tokens / 1_000_000
    return round(in_cost + out_cost, 6)
