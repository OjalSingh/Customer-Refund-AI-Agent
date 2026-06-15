from tools.user_tool import search_user
from tools.transaction_tool import get_transactions


user = search_user("U001")

print("User:")
print(user)

print()

transactions = get_transactions("U001")

print("Transactions:")
print(transactions)