from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from tools.policy_retriever import retrieve_policy


TOOLS = {
    "search_user": search_user,
    "get_transactions": get_transactions,
    "retrieve_policy": retrieve_policy,
}