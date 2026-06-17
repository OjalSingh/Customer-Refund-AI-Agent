def build_explanation(state):

    return {
        "summary": "Investigation completed",

        "intent": state.value("intent"),

        "evidence": {
            "transaction_count": len(state.value("transactions", [])),
            "risk_level": state.value("risk_result", {}).get("risk_level"),
            "risk_score": state.value("risk_result", {}).get("risk_score"),
            "policy_eligible": state.value("policy_result", {}).get("eligible"),
        },

        "decision": state.value("decision"),

        "key_reasons": state.value("audit_log")
    }