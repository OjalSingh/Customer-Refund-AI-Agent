import json

def get_transactions(user_id):

    with open("data/transactions.json") as f:
        txns = json.load(f)

    return [
        txn
        for txn in txns
        if txn["user_id"] == user_id
    ]