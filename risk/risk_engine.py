def assess_risk(user, transactions):

    score = 0
    reasons = []

    total_amount = sum(
        txn["amount"]
        for txn in transactions
    )

    if total_amount > 10000:
        score += 5
        reasons.append(
            "High transaction amount"
        )

    if len(transactions) > 5:
        score += 2
        reasons.append(
            "Multiple related transactions"
        )

    if score >= 5:

        level = "HIGH"

    elif score >= 2:

        level = "MEDIUM"

    else:

        level = "LOW"

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons
    }