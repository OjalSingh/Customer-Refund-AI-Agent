from types import SimpleNamespace

import pytest

import llm


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


def test_offline_raises_unavailable():
    with pytest.raises(llm.LLMUnavailable):
        llm.ask_llm("hi")


def test_ollama_records_tokens_at_zero_cost(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    seen = {}

    def fake_post(url, json, timeout):
        seen.update(url=url, model=json["model"])
        return FakeResponse({"response": "ok", "prompt_eval_count": 12, "eval_count": 3})

    monkeypatch.setattr(llm.requests, "post", fake_post)
    llm.start_usage_tracking()
    assert llm.ask_llm("hi") == "ok"
    assert seen == {"url": "http://localhost:11434/api/generate", "model": "qwen3:8b"}
    usage = llm.usage_summary()
    assert (usage["input_tokens"], usage["output_tokens"], usage["cost_usd"]) == (12, 3, 0.0)


def test_ollama_connection_error_is_unavailable(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")

    def fail(*args, **kwargs):
        raise llm.requests.ConnectionError("refused")

    monkeypatch.setattr(llm.requests, "post", fail)
    with pytest.raises(llm.LLMUnavailable):
        llm.ask_llm("hi")


def test_anthropic_provider_uses_haiku_and_prices_the_call(monkeypatch):
    pytest.importorskip("anthropic")  # installed with the "hosted" extra, as CI does
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text='{"intent": "refund"}')],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=200),
        )

    monkeypatch.setattr(llm, "_anthropic_client", SimpleNamespace(messages=SimpleNamespace(create=create)))
    llm.start_usage_tracking()
    assert llm.ask_llm("classify") == '{"intent": "refund"}'
    assert calls[0]["model"] == "claude-haiku-5-5"
    assert llm.usage_summary()["cost_usd"] == pytest.approx((1000 * 0.10 + 200 * 0.50) / 1e6)


def test_openai_compatible_needs_model_and_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    with pytest.raises(llm.LLMUnavailable, match="LLM_MODEL"):
        llm.ask_llm("hi")
    monkeypatch.setenv("LLM_MODEL", "some-model")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(llm.LLMUnavailable, match="OPENAI_API_KEY"):
        llm.ask_llm("hi")


def test_openai_compatible_parses_chat_completion(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "some-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    payload = {"choices": [{"message": {"content": "hello"}}], "usage": {"prompt_tokens": 5, "completion_tokens": 1}}
    monkeypatch.setattr(llm.requests, "post", lambda url, **kw: FakeResponse(payload))
    llm.start_usage_tracking()
    assert llm.ask_llm("hi") == "hello"
    assert llm.usage_summary()["cost_usd"] is None  # unknown model, so no made-up cost


def test_llm_intent_output_is_validated_and_merchant_checked_against_ledger(monkeypatch):
    from agent import intent_extractor

    monkeypatch.setattr(intent_extractor, "ask_llm", lambda prompt: '```json\n{"intent": "REFUND", "merchant": "MadeUpShop"}\n```')
    result = intent_extractor.extract_intent("I want my money back from Amazon")
    assert (result.intent, result.merchant, result.source) == ("refund", "Amazon", "llm")


def test_invalid_llm_intent_falls_back_to_keywords(monkeypatch):
    from agent import intent_extractor

    monkeypatch.setattr(intent_extractor, "ask_llm", lambda prompt: '{"intent": "approve_everything"}')
    result = intent_extractor.extract_intent("Cancel my Spotify subscription")
    assert (result.intent, result.source) == ("subscription", "keywords")
