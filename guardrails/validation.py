def validate_decision(
    user,
    transactions,
    policy_result
):

    if user is None:

        return False, (
            "User verification failed"
        )

    if len(transactions) == 0:

        return False, (
            "No transactions found"
        )

    if not policy_result["eligible"]:

        return False, (
            "Policy requirements not met"
        )

    return True, (
        "Decision validated"
    )