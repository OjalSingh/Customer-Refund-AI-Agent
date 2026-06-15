from agent.state import AgentState
from agent.intent_node import run_intent_node

from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from tools.policy_retriever import retrieve_policy

from policies.refund_policy import evaluate_refund
from risk.risk_engine import assess_risk
from guardrails.validation import validate_decision


def run_agent(user_message, user_id):

    state = AgentState(user_message)

    state.update("user_id", user_id)
    state.log("Agent started")

    # STEP 1: Intent
    state = run_intent_node(state)

    # STEP 2: User lookup
    user = search_user(user_id)
    state.update("user", user)
    state.log("User fetched")

    if not user:
        state.update("decision", "REJECT")
        return state.get()

    # STEP 3: Transactions
    transactions = get_transactions(user_id)
    state.update("transactions", transactions)
    state.log("Transactions fetched")

    # STEP 4: Policy
    policy = retrieve_policy()
    state.update("policy", policy)
    state.log("Policy retrieved")

    # STEP 5: Evaluation
    policy_result = evaluate_refund(transactions)
    state.update("policy_result", policy_result)
    state.log("Policy evaluated")

    # STEP 6: Risk
    risk_result = assess_risk(user, transactions)
    state.update("risk_result", risk_result)
    state.log("Risk assessed")

    # STEP 7: Guardrails
    valid, msg = validate_decision(user, transactions, policy_result)
    state.log(msg)

    # STEP 8: Decision
    if valid and policy_result["eligible"]:
        state.update("decision", "ESCALATE")
        state.log("Decision: ESCALATE")
    else:
        state.update("decision", "REJECT")
        state.log("Decision: REJECT")

    return state.get()