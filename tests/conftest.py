import pytest


@pytest.fixture(autouse=True)
def offline_llm(monkeypatch):
    """Tests never call a real model."""
    monkeypatch.setenv("LLM_PROVIDER", "offline")
