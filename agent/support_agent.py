from agent.state import AgentState
from agent.intent_node import run_intent_node

from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from tools.policy_retriever import retrieve_policy

from policies.refund_policy import evaluate_refund
from risk.risk_engine import assess_risk
from guardrails.validation import validate_decision
from agent.policy_reasoner import generate_explanation
from tools.document_retriever import retrieve_relevant_docs
from tools.document_loader import load_document_contents

def run_agent(user_message, user_id):

    state = AgentState(user_message)

    state.update("user_id", user_id)
    state.log("Agent started")

    #Intent
    state = run_intent_node(state)

    #Document Retrieval
    docs = retrieve_relevant_docs(
        state.value("intent", "")
    )

    state.update("retrieved_docs", docs)

    state.log(
        f"Retrieved docs: {docs}"
    )

    #Document Loader
    document_contents = load_document_contents(docs)
    state.update(
        "document_contents",
        document_contents
    )

    state.log(
        "Document contents loaded"
    )

    #User lookup
    user = search_user(user_id)
    state.update("user", user)
    state.log("User fetched")

    if not user:
        state.update(
            "risk_result",
            {
                "risk_level": "UNKNOWN",
                "risk_score": 0,
                "reasons": ["User not found"]
            }
        )

        state.log("User not found")
        state.update("decision", "REJECT")
        return state.get()


    #Transactions
    transactions = get_transactions(user_id)
    state.update("transactions", transactions)
    state.log("Transactions fetched")

    #Policy
    policy = retrieve_policy()
    state.update("policy", policy)
    state.log("Policy retrieved")

    #Evaluation
    policy_result = evaluate_refund(transactions)
    state.update("policy_result", policy_result)
    state.log("Policy evaluated")

    #Risk
    risk_result = assess_risk(user, transactions)
    state.update("risk_result", risk_result)
    state.log("Risk assessed")

    #Guardrails
    valid, msg = validate_decision(user, transactions, policy_result)
    state.log(msg)

    #Decision
    if valid and policy_result["eligible"]:
        state.update("decision", "ESCALATE")
        state.log("Decision: ESCALATE")
    else:
        state.update("decision", "REJECT")
        state.log("Decision: REJECT")
    
    #Policy explanation
    #explanation = generate_explanation(
    #    state.get()["document_contents"],
    #    transactions,
    #   policy_result,
    #    risk_result,
    #    state.get()["decision"]
    #)

    #state.update("explanation", explanation)
    #state.log("Explanation generated")

    return state.get()