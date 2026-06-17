from agent.support_agent import run_agent
from agent.report_generator import generate_report
from agent.intent_extractor import extract_intent
from agent.question_manager import get_questions


def main():

    print("\nREFUND SUPPORT AGENT\n")
    user_message = input("Customer Message: ")

    intent_data = extract_intent(user_message)
    intent = intent_data["intent"]
    print("DEBUG INTENT:", intent)

    questions = get_questions(intent)

    answers = {}

    for question in questions:
        answers[question] = input(f"Agent: {question}\nCustomer: ")

    user_id = input("Agent: Please provide your User ID: ")

    result = run_agent(
        user_message,
        user_id
    )

    report = generate_report(result)
    print(report)

if __name__ == "__main__":
    main()