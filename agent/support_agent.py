from agent.state import AgentState
from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from tools.policy_retriever import retrieve_policy_semantically
from agent.intent_node import run_intent_node
from agent.router import route_intent
from tools.investigation_engine import run_investigation
from policies.refund_policy import evaluate_refund_with_policy
from risk.risk_engine import assess_risk
from guardrails.validation import validate_decision
from tools.document_loader import load_document_contents
from agent.explanation_generator import build_explanation
from agent.explanation_llm import generate_explanation


# Change the function signature to accept follow_up_answers
def run_agent(user_message, user_id, follow_up_answers=None):

    state = AgentState(user_message)
    state.update("user_id", user_id)
    state.log("Agent started")
    
    # Store the follow-up answers inside state memory
    answers_dict = follow_up_answers or {}
    state.update("follow_up_answers", answers_dict)
    
    # Push answers into customer context memory layer for downstream evaluation
    for q, a in answers_dict.items():
        # Sanitize keys slightly so they are easy for the LLM to read
        clean_key = q.replace("?", "").lower().replace(" ", "_")
        state.update_customer_context(clean_key, a)

    # 1. Extract Intent & Routing
    state = run_intent_node(state)
    workflow = route_intent(state.value("intent"))
    state.update("workflow", workflow)
    state.log(f"Workflow selected: {workflow}")

    # 2. Fetch User Context
    user = search_user(user_id)
    state.update("user", user)

    if not user:
        state.update("decision", "REJECT")
        state.log("User not found")
        return state.get()

    # 3. Fetch Transaction Context
    transactions = get_transactions(user_id)
    state.update("transactions", transactions)

    # 4. Update Customer Memory Profile
    state.update_customer_context("total_transactions", len(transactions))
    state.update_customer_context("total_spend", sum(t["amount"] for t in transactions))

    # 5. Execute Background Engine Profiles
    investigation = run_investigation(transactions, user)
    state.update("investigation_result", investigation)

    risk_result = assess_risk(user, transactions)
    state.update("risk_result", risk_result)
    state.log("Baseline financial risk assessed")

    state.update_customer_context("risk_level", risk_result["risk_level"])
    state.update_customer_context("risk_score", risk_result["risk_score"])

    # 6. Retrieve Static Text Policy Rules
    policy = retrieve_policy_semantically(user_message=state.value("customer_message"), workflow=state.value("intent"))
    state.update("policy", policy)

    # ==========================================================
    # WORKFLOW RUNTIME LOGIC
    # ==========================================================
    if state.value("intent") in ["unknown", "greeting", "ambiguous"] or not workflow:
        state.update("decision", "AWAITING_CLARIFICATION")
        state.update("explanation", "Hello! I can help you with processing refunds, investigating unauthorized fraudulent charges, or managing your active subscriptions. Could you please provide more details or specify which transaction you are referring to?")
        state.log("Agent requested clarification from user")
        return state.get()
    
    if workflow in ["refund", "refund_request", "dispute"]:
        policy_result = evaluate_refund_with_policy(
            policy, 
            state.value("intent"), 
            state.value("transactions"),
            state.value("customer_context")
        )
        state.update("policy_result", policy_result)

        # Operational safety barrier verification
        valid, msg = validate_decision(state.value("user"), state.value("transactions"), policy_result)
        state.log(msg)

        # Enforce isolated guardrail conditional execution blocks
        if not valid:
            state.update("decision", "REJECT")
            state.log("Guardrail blocked decision → forced REJECT")
        elif policy_result.get("eligible"):
            state.update("decision", "ESCALATE")
            state.log("Refund approved for escalation")
        else:
            state.update("decision", "REJECT")
            state.log("Refund rejected per policy rules")

    elif workflow == "fraud":
        if investigation.get("duplicate") or investigation.get("high_value"):
            state.update("decision", "ESCALATE")
            state.log("Fraud detected → Escalate to Risk Operations")
        else:
            state.update("decision", "REJECT")
            state.log("No explicit fraud signals matched")

    # Subscription Evaluation Loop
    elif workflow == "subscription":
        state.log("Executing subscription policy evaluation...")
        
        # Look for subscription keywords or indicators in active transactions
        has_active_subscription = any("netflix" in str(t.get("merchant", "")).lower() for t in transactions)
        
        # Check if they explicitly asked to cancel or stop it
        msg_lower = user_message.lower()
        if "cancel" in msg_lower or "stop" in msg_lower or "unsubscribe" in msg_lower:
            state.update("decision", "ESCALATE")
            state.log("Valid subscription cancellation intent → Escalate for processing")
        elif has_active_subscription:
            state.update("decision", "REJECT")
            state.update("explanation", "I see an active billing agreement on your profile, but I'm not sure what you'd like me to do with it. Would you like to cancel your subscription or dispute a specific charge?")
            state.log("Subscription found but action unclear")
        else:
            state.update("decision", "REJECT")
            state.log("No matching subscription agreements found on record")

    else:
        state.update("decision", "REJECT")
        state.log("Unknown workflow state matched")

    # 7. Post-Execution Pipeline Reports & Explanations Generation
    structured_explanation = build_explanation(state)
    state.update("structured_explanation", structured_explanation)
    state.log("Structured explanation generated")

    llm_explanation = generate_explanation(state)
    state.update("explanation", llm_explanation)
    state.log("LLM conversation layer response created")

    return state.get()