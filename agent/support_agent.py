

from tools.investigation_engine import run_investigation
from policies.refund_policy import evaluate_refund
from risk.risk_engine import assess_risk
from guardrails.validation import validate_decision
from agent.explanation_llm import generate_explanation
from tools.document_retriever import retrieve_relevant_docs
from tools.document_loader import load_document_contents
from agent.explanation_generator import build_explanation
from agent.explanation_llm import generate_explanation


def run_agent(user_message, user_id):

    state = AgentState(user_message)

    state.update("user_id", user_id)
    state.log("Agent started")

    # Intent
    state = run_intent_node(state)

    workflow = route_intent(state.get()["intent"])
    state.update("workflow", workflow)
    state.log(f"Workflow selected: {workflow}")

    # User
    user = search_user(user_id)
    state.update("user", user)

    if not user:
        state.update("decision", "REJECT")
        state.log("User not found")
        return state.get()

    # Transactions
    transactions = get_transactions(user_id)
    state.update("transactions", transactions)


    # MEMORY UPDATE
    state.update_customer_context(
        "total_transactions",
        len(transactions)
    )

    state.update_customer_context(
        "total_spend",
        sum(t["amount"] for t in transactions)
    )

    # Common investigation (used by all workflows)
    investigation = run_investigation(transactions, user)
    state.update("investigation_result", investigation)

    # Policy (load once)
    policy = retrieve_policy()
    state.update("policy", policy)

    # =========================
    # WORKFLOW ROUTING
    # =========================

    if workflow == "refund":

        policy_result = evaluate_refund(transactions)

        risk_result = assess_risk(user, transactions)

        valid, msg = validate_decision(user, transactions, policy_result)
        state.log(msg)

        #GUARDRAIL ENFORCEMENT
        if not valid:
            state.update("decision", "REJECT")
            state.log("Guardrail blocked decision → forced REJECT")

        if valid and policy_result["eligible"]:
            state.update("decision", "ESCALATE")
            state.log("Refund approved")
        else:
            state.update("decision", "REJECT")
            state.log("Refund rejected")

    elif workflow == "fraud":

        if investigation["duplicate"] or investigation["high_value"]:
            state.update("decision", "ESCALATE")
            state.log("Fraud detected → Escalate")
        else:
            state.update("decision", "REJECT")
            state.log("No fraud signals found")

    elif workflow == "subscription":

        state.update("decision", "REJECT")
        state.log("Subscription workflow (stub)")

    else:
        state.update("decision", "REJECT")
        state.log("Unknown workflow")

    # Risk always computed (optional but consistent)
    state.update("risk_result", risk_result)
    state.log("Risk assessed")

    # MEMORY UPDATE (ADD HERE)
    state.update_customer_context(
        "risk_level",
        risk_result["risk_level"]
    )

    state.update_customer_context(
        "risk_score",
        risk_result["risk_score"]
    )

    # Structured explanation (truth layer)
    structured_explanation = build_explanation(state)
    state.update("structured_explanation", structured_explanation)
    state.log("Structured explanation generated")

    # LLM explanation (human layer)
    llm_explanation = generate_explanation(state)
    state.update("explanation", llm_explanation)
    state.log("LLM explanation generated")

    return state.get()
