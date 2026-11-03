"""LLM access for the agent, behind one ask_llm() call.

Choose the backend with LLM_PROVIDER (and optionally LLM_MODEL):

  ollama     (default) local model through Ollama; nothing leaves the machine.
             LLM_MODEL defaults to qwen3:8b, OLLAMA_URL to http://localhost:11434
  anthropic  Claude through the Anthropic API (needs ANTHROPIC_API_KEY).
             LLM_MODEL defaults to claude-haiku-5-5
  openai     any OpenAI-compatible chat endpoint, e.g. Gemini, Groq, vLLM or
             LM Studio. Set OPENAI_BASE_URL, OPENAI_API_KEY and LLM_MODEL
             (OPENAI_BASE_URL defaults to Gemini's OpenAI-compatible endpoint)
  offline    no model at all; keyword intent extraction and template
             explanations (CI and the eval baseline)

The policy engine never depends on the model, so every provider gets the same
guardrails; only intent extraction and the wording of explanations change.

Every call records its token usage and estimated cost, which run_agent()
returns in state["llm_usage"].
"""

import contextvars
import os
import time
from dataclasses import asdict, dataclass

import requests


class LLMUnavailable(RuntimeError):
    """Raised when no model is configured or reachable, so callers fall back to deterministic code."""


DEFAULT_MODELS = {
    "ollama": "qwen3:8b",
    "anthropic": "claude-haiku-5-5",
}

# USD per million tokens (input, output). Local models cost nothing per call.
# Update these from the provider's pricing page when you change models.
PRICES_PER_MTOK = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}


@dataclass
class LLMCall:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    seconds: float
    cost_usd: float | None


_calls: contextvars.ContextVar[list | None] = contextvars.ContextVar("llm_calls", default=None)


def start_usage_tracking():
    """Begin collecting LLMCall records for the current request (one agent run)."""
    _calls.set([])


def usage_summary():
    calls = _calls.get() or []
    unpriced = any(c.cost_usd is None for c in calls)
    return {
        "calls": [asdict(c) for c in calls],
        "input_tokens": sum(c.input_tokens for c in calls),
        "output_tokens": sum(c.output_tokens for c in calls),
        # None when a model has no entry in PRICES_PER_MTOK, rather than a misleading partial total
        "cost_usd": None if unpriced else round(sum(c.cost_usd for c in calls), 6),
    }


def provider_name():
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def model_name(provider=None):
    provider = provider or provider_name()
    return os.getenv("LLM_MODEL") or DEFAULT_MODELS.get(provider, "")


def ask_llm(prompt, max_tokens=1024):
    provider = provider_name()
    backends = {"ollama": _ask_ollama, "anthropic": _ask_anthropic, "openai": _ask_openai_compatible}
    if provider == "offline":
        raise LLMUnavailable("LLM_PROVIDER=offline")
    if provider not in backends:
        raise LLMUnavailable(f"Unknown LLM_PROVIDER '{provider}'")

    model = model_name(provider)
    if not model:
        raise LLMUnavailable(f"Set LLM_MODEL for LLM_PROVIDER={provider}")
    started = time.perf_counter()
    text, input_tokens, output_tokens = backends[provider](prompt, model, max_tokens)
    _record(provider, model, input_tokens, output_tokens, time.perf_counter() - started)
    return text


def _record(provider, model, input_tokens, output_tokens, seconds):
    calls = _calls.get()
    if calls is None:
        return
    cost = 0.0 if provider == "ollama" else None
    if model in PRICES_PER_MTOK:
        price_in, price_out = PRICES_PER_MTOK[model]
        cost = (input_tokens * price_in + output_tokens * price_out) / 1_000_000
    calls.append(LLMCall(provider, model, input_tokens, output_tokens, round(seconds, 3), cost))


def _ask_ollama(prompt, model, max_tokens):
    url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate"
    try:
        response = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": max_tokens}},
            timeout=300,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMUnavailable(f"Ollama request failed: {exc}") from exc
    data = response.json()
    return data["response"], data.get("prompt_eval_count", 0), data.get("eval_count", 0)


_anthropic_client = None


def _ask_anthropic(prompt, model, max_tokens):
    global _anthropic_client
    try:
        import anthropic
    except ImportError as exc:
        raise LLMUnavailable("Install the hosted extra: pip install anthropic") from exc

    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()
    try:
        response = _anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            output_config={"effort": "low"},  # extraction and short explanations do not need deep thinking
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIConnectionError as exc:
        raise LLMUnavailable(f"Anthropic API unreachable: {exc}") from exc
    except anthropic.APIStatusError as exc:
        raise LLMUnavailable(f"Anthropic API error {exc.status_code}: {exc.message}") from exc

    if response.stop_reason == "refusal":
        raise LLMUnavailable("Model declined the request")
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, response.usage.input_tokens, response.usage.output_tokens


def _ask_openai_compatible(prompt, model, max_tokens):
    base_url = os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai").rstrip("/")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMUnavailable("Set OPENAI_API_KEY for LLM_PROVIDER=openai")
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]},
            timeout=120,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMUnavailable(f"OpenAI-compatible request failed: {exc}") from exc
    data = response.json()
    usage = data.get("usage") or {}
    return data["choices"][0]["message"]["content"], usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
