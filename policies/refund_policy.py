def evaluate_refund(transactions):

    if len(transactions) < 2:
        return False

    first = transactions[0]
    second = transactions[1]

    same_amount = (
        first["amount"] == second["amount"]
    )

    same_merchant = (
        first["merchant"] == second["merchant"]
    )

    both_success = (
        first["status"] == "SUCCESS"
        and
        second["status"] == "SUCCESS"
    )

    return (
        same_amount
        and same_merchant
        and both_success
    )