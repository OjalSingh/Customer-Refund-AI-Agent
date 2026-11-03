from agent import policy_engine
from agent.explanation_generator import build_explanation
from agent.explanation_llm import generate_explanation
from agent.intent_node import run_intent_node
from agent.router import route_intent
from agent.state import AgentState
from guardrails.injection import detect_prompt_injection
from guardrails.validation import validate_decision
from risk.risk_engine import assess_risk
from tools.investigation_engine import run_investigation
from tools.policy_clauses import clause_text
from tools.policy_retriever import retrieve_policy_semantically
from tools.transaction_tool import get_transactions
from tools.user_tool import search_user


def run_agent(user_message, user_id, follow_up_answers=None, explain=True):
    """Run one customer request through the pipeline and return the final state dict.

    explain=False skips the LLM explanation step (the eval suite uses this to
    score decisions quickly).
    """
    state = AgentState(user_message)
    state.update("user_id", user_id)
    state.log("Agent started")

    answers = follow_up_answers or {}
    state.update("follow_up_answers", answers)
    for question, answer in answers.items():
        state.update_customer_context(question.replace("?", "").lower().replace(" ", "_"), answer)

    # 1. Guardrail: screen the raw message before any model sees it.
    full_text = " ".join([user_message, *map(str, answers.values())])
    injection = detect_prompt_injection(full_text)
    state.update("injection_detected", bool(injection))
    if injection:
        state.update("intent", "prompt_injection")
        state.log("Prompt-injection pattern detected → LLM skipped")
    else:
        # 2. LLM extracts what the customer wants (intent + merchant). Nothing else.
        state = run_intent_node(state)

    workflow = route_intent(state.value("intent"))
    state.update("workflow", workflow)
    state.log(f"Workflow selected: {workflow}")

    # 3. Pull ledger context.
    user = search_user(user_id)
    transactions = get_transactions(user_id) if user else []
    state.update("user", user)
    state.update("transactions", transactions)
    state.update_customer_context("total_transactions", len(transactions))
    state.update_customer_context("total_spend", round(sum(t["amount"] for t in transactions), 2))

    state.update("investigation_result", run_investigation(transactions, user))
    risk_result = assess_risk(user, transactions)
    state.update("risk_result", risk_result)
    state.update_customer_context("risk_level", risk_result["risk_level"])
    state.log("Baseline financial risk assessed")

    # 4. Deterministic policy engine makes the decision.
    result = policy_engine.evaluate(
        intent=state.value("intent"),
        user=user,
        transactions=transactions,
        merchant=state.value("merchant"),
        injection=injection,
    )
    valid, msg = validate_decision(user, transactions, result)
    if not valid:
        state.log(f"Guardrail override: {msg}")
        result = policy_engine.PolicyDecision(policy_engine.REJECT, result.clause, [*result.reasons, msg])

    state.update("policy_decision", result.to_dict())
    state.update("policy_result", {"eligible": result.decision == policy_engine.APPROVE, "reasoning": result.reasons})
    state.update("decision", result.decision)
    state.update("policy_clause", result.clause)
    state.update("policy", clause_text(result.clause) or "No policy clause applied.")
    state.log(f"Policy engine: {result.decision} under {result.clause or 'no clause'}")

    if result.decision == policy_engine.AWAITING_CLARIFICATION:
        state.update(
            "explanation",
            "I can help with refunds, unauthorized or duplicate charges, and cancelling subscriptions or orders. "
            "Could you tell me what happened and which merchant the charge was from?",
        )
        return state.get()

    # 5. Supporting context and explanation (never changes the decision).
    if not injection:
        state.update("retrieved_policy", retrieve_policy_semantically(user_message, workflow=workflow))

    state.update("structured_explanation", build_explanation(state))
    if explain:
        state.update("explanation", generate_explanation(state))
        state.log("Explanation generated")

    return state.get()
