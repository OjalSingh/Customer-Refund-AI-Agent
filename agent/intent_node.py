from agent.intent_extractor import extract_intent


def run_intent_node(state):
    result = extract_intent(state.value("user_message"))
    state.update("intent", result.intent)
    state.update("merchant", result.merchant)
    state.log(f"Intent '{result.intent}' extracted via {result.source}" + (f" (merchant: {result.merchant})" if result.merchant else ""))
    return state
