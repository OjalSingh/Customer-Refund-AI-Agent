from agent.support_agent import run_agent
from agent.report_generator import generate_report


def main():

    print("\nREFUND SUPPORT AGENT\n")

    user_message = input("Customer Message: ")
    user_id = input(
        "Agent: Please provide your User ID: "
    )

    result = run_agent(user_message, user_id)

    report = generate_report(result)
    print(report)

if __name__ == "__main__":
    main()