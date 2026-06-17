def route_intent(intent: str):

    intent = intent.lower().strip()

    if "refund" in intent:
        return "refund"

    if "fraud" in intent:
        return "fraud"

    if "exchange" in intent:
        return "exchange"

    if "subscription" in intent:
        return "subscription"

    return "unknown"