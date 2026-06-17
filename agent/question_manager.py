def get_questions(intent):

    intent = intent.lower()

    if intent == "refund":
        return [
            "What is the reason for your refund request?",
            "Which merchant was involved?"
        ]

    return []