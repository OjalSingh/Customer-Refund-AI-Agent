import json

from agent.paths import DATA_DIR


def get_transactions(user_id):
    with open(DATA_DIR / "transactions.json", encoding="utf-8") as f:
        transactions = json.load(f)

    return [txn for txn in transactions if txn["user_id"] == user_id]


def known_merchants():
    """Every merchant name that appears in the ledger, used to match merchants in messages."""
    with open(DATA_DIR / "transactions.json", encoding="utf-8") as f:
        transactions = json.load(f)

    return sorted({txn["merchant"] for txn in transactions})
