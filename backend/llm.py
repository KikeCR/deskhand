"""Builds the crew's chat LLM with automatic fallback across providers.

This is only about chat completions (the 3 CrewAI agents). RAG embeddings
(rag/ingest.py) are a separate, unrelated pipeline that runs on a free
local model, so none of this affects embedding cost or behavior.

An operator can have credits on OpenAI, DeepSeek, Kimi (Moonshot), or any
combination. LLM_PROVIDERS controls which ones are tried and in what
order; a provider is skipped automatically if its API key isn't set, so
setting only DEEPSEEK_API_KEY is enough to run the whole crew on DeepSeek.
"""

from __future__ import annotations

import os

from crewai import LLM


class ProviderUnavailable(Exception):
    pass


def _build_openai_llm() -> LLM | None:
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return LLM(model=model)


def _build_deepseek_llm() -> LLM | None:
    if not os.environ.get("DEEPSEEK_API_KEY"):
        return None
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    # crewai's native "deepseek" provider reads DEEPSEEK_API_KEY /
    # DEEPSEEK_BASE_URL from the environment itself.
    return LLM(model=f"deepseek/{model}")


def _build_kimi_llm() -> LLM | None:
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        return None
    model = os.environ.get("KIMI_MODEL", "moonshot-v1-8k")
    base_url = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
    # Kimi/Moonshot has no native provider in crewai but exposes an
    # OpenAI-compatible API, so route it through the custom-endpoint path.
    return LLM(model=model, custom_openai=True, base_url=base_url, api_key=api_key)


PROVIDER_BUILDERS = {
    "openai": _build_openai_llm,
    "deepseek": _build_deepseek_llm,
    "kimi": _build_kimi_llm,
}

DEFAULT_PROVIDER_ORDER = "openai,deepseek,kimi"


def build_llm_chain() -> list[tuple[str, LLM]]:
    """Return (provider_name, LLM) pairs to try in order.

    Order and membership come from LLM_PROVIDERS (comma-separated). Any
    provider without its API key set is skipped rather than erroring, so
    the chain naturally shrinks to whatever the operator actually has
    credit for.
    """
    order = [
        name.strip().lower()
        for name in os.environ.get("LLM_PROVIDERS", DEFAULT_PROVIDER_ORDER).split(",")
        if name.strip()
    ]

    chain = []
    for name in order:
        builder = PROVIDER_BUILDERS.get(name)
        if builder is None:
            continue
        candidate = builder()
        if candidate is not None:
            chain.append((name, candidate))

    if not chain:
        raise ProviderUnavailable(
            "No LLM provider is configured. Set one of OPENAI_API_KEY, "
            "DEEPSEEK_API_KEY, or KIMI_API_KEY in backend/.env."
        )
    return chain
