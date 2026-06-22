def build_explanation(state):
    # Fetch values safely, forcing fallback defaults if the value itself is None
    policy_res = state.value("policy_result") or {}
    risk_res = state.value("risk_result") or {}
    txns = state.value("transactions") or []

    return {
        "summary": "Investigation completed",

        "intent": state.value("intent"),

        "evidence": {
            "transaction_count": len(txns),
            "risk_level": risk_res.get("risk_level"),
            "risk_score": risk_res.get("risk_score"),
            "policy_eligible": policy_res.get("eligible"),
        },

        "decision": state.value("decision"),

        "key_reasons": state.value("audit_log", [])
    }