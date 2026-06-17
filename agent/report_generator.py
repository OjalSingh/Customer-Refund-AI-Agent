def generate_report(state):

    lines = []

    lines.append("=" * 50)
    lines.append("INVESTIGATION REPORT")
    lines.append("=" * 50)

    lines.append(f"\nUser ID: {state['user_id']}")
    lines.append(f"Intent: {state['intent']}")
    lines.append(f"Decision: {state['decision']}")

    if state["risk_result"]:

        lines.append(
            f"Risk Level: {state['risk_result']['risk_level']}"
        )

        lines.append(
            f"Risk Score: {state['risk_result']['risk_score']}"
        )

        if state["risk_result"]["reasons"]:

            lines.append("\nRisk Findings:")

            for reason in state["risk_result"]["reasons"]:
                lines.append(f"- {reason}")

    if state["policy_result"]:

        lines.append("\nPolicy Findings:")

        for reason in state["policy_result"]["reasoning"]:
            lines.append(f"- {reason}")
    
    if state["explanation"]:

        lines.append("\nExplanation:")

        lines.append(state["explanation"])

    lines.append("\nAudit Trail:")

    for log in state["audit_log"]:
        lines.append(f"- {log}")

    return "\n".join(lines)