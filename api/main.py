"""HTTP API and demo web UI for the refund agent.

    uvicorn api.main:app --reload        # then open http://localhost:8000
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent.paths import DATA_DIR
from agent.support_agent import run_agent
from llm import model_name, provider_name
from tools.transaction_tool import get_transactions

STATIC_DIR = Path(__file__).with_name("static")

app = FastAPI(
    title="Refund and fraud-review agent",
    description="An LLM reads the request; a deterministic policy engine makes the decision and cites the clause.",
    version="0.3.0",
)


class ReviewRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=32, examples=["U001"])
    message: str = Field(min_length=1, max_length=2000, examples=["I got charged twice by Netflix"])
    follow_up_answers: dict[str, str] | None = None


class ReviewResponse(BaseModel):
    decision: str
    policy_clause: str | None
    policy_text: str
    reasons: list[str]
    target_txn_ids: list[str]
    intent: str | None
    merchant: str | None
    injection_detected: bool
    explanation: str | None
    audit_log: list[str]
    transactions: list[dict]
    llm: dict
    llm_usage: dict


@app.get("/health")
def health():
    return {"status": "ok", "provider": provider_name(), "model": model_name() or None}


@app.get("/api/customers")
def customers():
    """Demo customers with their ledgers, so the UI can show what the agent sees."""
    users = json.loads((DATA_DIR / "users.json").read_text(encoding="utf-8"))
    return [
        {"user_id": u["user_id"], "name": u["name"], "status": u["status"], "tier": u["tier"], "transactions": get_transactions(u["user_id"])}
        for u in users
    ]


@app.post("/api/review", response_model=ReviewResponse)
def review(request: ReviewRequest):
    try:
        state = run_agent(request.message, request.user_id.strip().upper(), follow_up_answers=request.follow_up_answers)
    except Exception as exc:  # never leak a stack trace to the client
        raise HTTPException(status_code=500, detail="Agent failed to process the request") from exc

    result = state.get("policy_decision") or {}
    return ReviewResponse(
        decision=state["decision"],
        policy_clause=state.get("policy_clause"),
        policy_text=state.get("policy") or "",
        reasons=result.get("reasons", []),
        target_txn_ids=result.get("target_txn_ids", []),
        intent=state.get("intent"),
        merchant=state.get("merchant"),
        injection_detected=state.get("injection_detected", False),
        explanation=state.get("explanation"),
        audit_log=state.get("audit_log", []),
        transactions=state.get("transactions", []),
        llm=state.get("llm", {}),
        llm_usage=state.get("llm_usage") or {},
    )


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
