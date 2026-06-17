def run_investigation(transactions, user):

    signals = {
        "duplicate": False,
        "high_value": False,
        "velocity": False,
        "reasons": []
    }

    if not transactions:
        return signals

    # 1. Duplicate detection
    for i in range(len(transactions)):
        for j in range(i + 1, len(transactions)):

            a, b = transactions[i], transactions[j]

            if (
                a["merchant"] == b["merchant"]
                and a["amount"] == b["amount"]
                and a["status"] == "SUCCESS"
                and b["status"] == "SUCCESS"
            ):
                signals["duplicate"] = True
                signals["reasons"].append("Duplicate transaction detected")
                break

    # 2. High value check
    total = sum(t["amount"] for t in transactions)

    if total > 10000:
        signals["high_value"] = True
        signals["reasons"].append("High transaction volume detected")

    # 3. Velocity check (simple version)
    if len(transactions) > 5:
        signals["velocity"] = True
        signals["reasons"].append("High transaction frequency detected")

    return signals