import json
from llm import ask_llm


def plan_next_action(state):

    if state["user"] is None:
        return {"action": "search_user"}

    if not state["transactions"]:
        return {"action": "get_transactions"}

    if state["policy"] is None:
        return {"action": "retrieve_policy"}

    return {"action": "finish"}