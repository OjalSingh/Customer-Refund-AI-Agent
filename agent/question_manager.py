def get_missing_fields(state):

    missing = []

    if not state["merchant"]:
        missing.append("merchant")

    if not state["user_id"]:
        missing.append("user_id")

    return missing