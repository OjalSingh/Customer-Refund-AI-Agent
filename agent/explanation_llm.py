from llm import LLMUnavailable, ask_llm


def template_explanation(state):
    """Plain explanation built only from the engine's output. Used when no LLM is available."""
    result = state.value("policy_decision") or {}
    reasons = result.get("reasons") or []
    lines = [
        f"Decision: {state.value('decision')}",
        f"Policy applied: {result.get('clause') or 'none'}",
    ]
    if result.get("target_txn_ids"):
        lines.append("Transactions reviewed: " + ", ".join(result["target_txn_ids"]))
    lines += [f"- {r}" for r in reasons]
    return "\n".join(lines)


def generate_explanation(state):
    result = state.value("policy_decision") or {}
    prompt = f"""You are a support investigation analyst writing to a customer-operations reviewer.

The decision below is FINAL. It was made by a rule-based policy engine. Explain it; do not change it,
question it, or suggest a different outcome. Use only the data provided.

INTENT: {state.value("intent")}
DECISION: {state.value("decision")}
POLICY CLAUSE APPLIED: {result.get("clause")}
POLICY TEXT:
{state.value("policy")}
ENGINE REASONS: {result.get("reasons")}
TRANSACTIONS: {state.value("transactions")}
RISK RESULT: {state.value("risk_result")}

Write a concise, professional explanation with these sections:
1. Summary of what happened
2. Evidence considered
3. Why this decision was made (name the policy clause)
4. Next step
"""
    try:
        return ask_llm(prompt)
    except LLMUnavailable:
        return template_explanation(state)
