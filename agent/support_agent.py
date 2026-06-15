from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from policies.refund_policy import evaluate_refund


def investigate_refund(user_id):

    print("Searching user...")

    user = search_user(user_id)

    if not user:
        return {
            "decision": "REJECT",
            "reason": "User not found"
        }

    print("User found")

    print("Fetching transactions...")

    transactions = get_transactions(user_id)

    result = evaluate_refund(transactions)

    if result["eligible"]:

        return {
            "decision": "ESCALATE",
            "reasoning": result["reasoning"]
        }

    return {
        "decision": "REJECT",
        "reasoning": result["reasoning"]
    }