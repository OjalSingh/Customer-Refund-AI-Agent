from agent.support_agent import run_agent
from agent.report_generator import generate_report
from agent.intent_extractor import extract_intent
from agent.question_manager import get_dynamic_questions
from tools.policy_retriever import retrieve_policy

def main():
    print("\n⚡ REASONING REFUND AGENT INTERFACE ⚡\n")
    user_message = input("Customer Message: ")

    # 1. Classify intent dynamically
    intent_data = extract_intent(user_message)
    intent = intent_data.get("intent", "unknown")
    print("DEBUG INTENT:", intent)

    # 2. Grab raw policy guidelines to see what data fields we need
    # (Reads policies/refund_policy.txt, etc.)
    policy_text = retrieve_policy() 

    # 3. Ask the LLM to dynamically audit the missing details
    questions = get_dynamic_questions(intent, user_message, policy_text)
    answers = {}

    # 4. Collect answers naturally without menus
    if questions:
        print("\n--- Clarification Needed ---")
        for question in questions:
            answers[question] = input(f"Agent: {question}\nCustomer: ")
        print("----------------------------\n")

    user_id = input("Agent: Please provide your User ID to pull transaction context: ")

    # 5. Hand the entire bundle over to the core state engine
    result = run_agent(
        user_message=user_message,
        user_id=user_id,
        follow_up_answers=answers
    )

    report = generate_report(result)
    print(report)

if __name__ == "__main__":
    main()