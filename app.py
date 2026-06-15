from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from policies.refund_policy import evaluate_refund


user = search_user("U001")

transactions = get_transactions("U001")

result = evaluate_refund(transactions)

print(result)