def route_intent(intent):
    intent = (intent or "").lower().strip()

    if "refund" in intent:
        return "refund"
    if "fraud" in intent:
        return "fraud"
    if "subscription" in intent or "cancel" in intent:
        return "cancellation"

    return "unknown"
