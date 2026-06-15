from tools.user_tool import search_user
from tools.transaction_tool import get_transactions
from tools.policy_retriever import retrieve_policy

from policies.refund_policy import evaluate_refund

from risk.risk_engine import assess_risk

from guardrails.validation import validate_decision


def main():

    print("=" * 50)
    print("REFUND SUPPORT AGENT")
    print("=" * 50)

    user_id = input("\nEnter User ID: ")

    print("\n[1] Searching user...")

    user = search_user(user_id)

    if not user:
        print("User not found")
        return

    print(f"User Found: {user['name']}")

    print("\n[2] Fetching transactions...")

    transactions = get_transactions(user_id)

    print(
        f"{len(transactions)} transaction(s) found"
    )

    print("\n[3] Retrieving policy...")

    policy = retrieve_policy()

    print("Policy loaded successfully")

    print("\n[4] Evaluating refund policy...")

    policy_result = evaluate_refund(
        transactions
    )

    print(
        f"Eligible: {policy_result['eligible']}"
    )

    print("\n[5] Assessing risk...")

    risk_result = assess_risk(
        user,
        transactions
    )

    print(
        f"Risk Level: {risk_result['risk_level']}"
    )

    print("\n[6] Running guardrails...")

    valid, message = validate_decision(
        user,
        transactions,
        policy_result
    )

    print(message)

    print("\n" + "=" * 50)
    print("INVESTIGATION REPORT")
    print("=" * 50)

    print(f"\nUser ID: {user['user_id']}")
    print(f"Name: {user['name']}")

    print(
        f"\nTransactions Found: "
        f"{len(transactions)}"
    )

    print("\nPolicy Evaluation:")

    for reason in policy_result["reasoning"]:
        print(f"✓ {reason}")

    print(
        f"\nRisk Level: "
        f"{risk_result['risk_level']}"
    )

    if risk_result["reasons"]:

        print("\nRisk Factors:")

        for reason in risk_result["reasons"]:
            print(f"- {reason}")

    if valid and policy_result["eligible"]:

        decision = "ESCALATE"

    else:

        decision = "REJECT"

    print(f"\nDecision: {decision}")

    print("\nPolicy Source:")
    print("refund_policy.txt")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()