def evaluate_refund(transactions):

    reasoning = []

    if len(transactions) < 2:
        return {
            "eligible": False,
            "reasoning": ["Less than two transactions found"]
        }

    txn1 = transactions[0]
    txn2 = transactions[1]

    if txn1["merchant"] == txn2["merchant"]:
        reasoning.append("Same merchant")
    else:
        return {
            "eligible": False,
            "reasoning": ["Different merchants"]
        }

    if txn1["amount"] == txn2["amount"]:
        reasoning.append("Same amount")
    else:
        return {
            "eligible": False,
            "reasoning": ["Different amounts"]
        }

    if (
        txn1["status"] == "SUCCESS"
        and txn2["status"] == "SUCCESS"
    ):
        reasoning.append("Both transactions successful")
    else:
        return {
            "eligible": False,
            "reasoning": ["One or more transactions failed"]
        }

    return {
        "eligible": True,
        "reasoning": reasoning
    }