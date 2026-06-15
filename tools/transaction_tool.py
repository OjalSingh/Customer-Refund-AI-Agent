import json


def get_transactions(user_id):

    with open("data/transactions.json", "r") as f:
        transactions = json.load(f)

    return [
        txn
        for txn in transactions
        if txn["user_id"] == user_id
    ]