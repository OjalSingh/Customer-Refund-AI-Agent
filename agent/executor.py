from agent.tool_registry import TOOLS


def execute_action(action, state):

    action_name = action["action"]
    print(
        f"Executing {action_name}"
    )

    if action_name == "search_user":

        user = TOOLS[action_name](
            state["user_id"]
        )

        state["user"] = user

    elif action_name == "get_transactions":

        txns = TOOLS[action_name](
            state["user_id"]
        )

        state["transactions"] = txns

    elif action_name == "retrieve_policy":

        policy = TOOLS[action_name]()

        state["policy"] = policy

    return state

