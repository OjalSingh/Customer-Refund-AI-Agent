from agent.intent_extractor import extract_intent


def run_intent_node(state):

    result = extract_intent(state.state["user_message"])

    state.update("intent", result["intent"])
    state.update("merchant", result["merchant"])

    state.log("Intent extracted using Qwen")

    return state