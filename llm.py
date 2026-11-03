"""LLM access for the agent.

Set LLM_PROVIDER to choose the backend:
  ollama  (default) local model through Ollama, nothing leaves the machine
  offline no model at all; the agent uses keyword intent extraction and
          template explanations (used by CI and the eval suite's baseline)

The policy engine never depends on the model, so every provider gives the same
guardrails; only intent extraction and the wording of explanations change.
"""

import os

import requests


class LLMUnavailable(RuntimeError):
    """Raised when no model is configured, so callers can fall back to deterministic code."""


def provider_name():
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def ask_llm(prompt):
    provider = provider_name()
    if provider == "offline":
        raise LLMUnavailable("LLM_PROVIDER=offline")
    if provider == "ollama":
        return _ask_ollama(prompt)
    raise LLMUnavailable(f"Unknown LLM_PROVIDER '{provider}'")


def _ask_ollama(prompt):
    url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate"
    model = os.getenv("LLM_MODEL", "qwen3:8b")
    try:
        response = requests.post(url, json={"model": model, "prompt": prompt, "stream": False}, timeout=300)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMUnavailable(f"Ollama request failed: {exc}") from exc
    return response.json()["response"]
