from agent.support_agent import run_agent


def main():

    print("\nREFUND SUPPORT AGENT\n")

    user_message = input("Customer Message: ")
    user_id = input("User ID: ")

    result = run_agent(user_message, user_id)

    print("\nFINAL DECISION:", result["decision"])

    print("\n--- AUDIT TRAIL ---")
    for i, log in enumerate(result["audit_log"], 1):
        print(f"{i}. {log}")

    print("\n--- INTENT ---")
    print(result["intent"])

    print("\n--- RISK ---")
    print(result["risk_result"]["risk_level"])


if __name__ == "__main__":
    main()