def evaluate_refund(transactions):

    reasoning = []

    if len(transactions) < 2:
        return {
            "eligible": False,
            "reasoning": ["Less than two transactions found"]
        }

    for i in range(len(transactions)):
        for j in range(i + 1, len(transactions)):

            txn1 = transactions[i]
            txn2 = transactions[j]

        if (
            txn1["merchant"] == txn2["merchant"]
            and txn1["amount"] == txn2["amount"]
            and txn1["status"] == "SUCCESS"
            and txn2["status"] == "SUCCESS"
        ):
            return {
                "eligible": True,
                "reasoning": [
                    "Duplicate transaction detected",
                    f"Merchant: {txn1['merchant']}",
                    f"Amount: {txn1['amount']}"
                ]
            }

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