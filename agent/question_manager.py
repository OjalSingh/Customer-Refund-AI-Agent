import json
from llm import ask_llm

def get_dynamic_questions(intent, user_message, policy_text):
    """
    Dynamically analyzes what information is missing based on the text policy
    and the user's initial message.
    """
    if intent == "unknown":
        return ["Could you please clarify what you need help with today (e.g., refund, cancellation, billing dispute)?"]

    prompt = f"""[System: Support Triage Engine. Identify missing data fields required by the policy. Max 2 questions.]

### POLICY REQUIREMENTS
{policy_text}

### CUSTOMER INITIAL MESSAGE
"{user_message}"

### TASK
Look at the policy criteria and the customer's message. What critical information is missing to evaluate this case?
Generate a JSON array containing up to 2 specific, natural questions to ask the user.
If no critical information is missing, return an empty array [].

Schema:
["Question 1?", "Question 2?"]

JSON:"""

    response = ask_llm(prompt).strip()
    try:
        if "```" in response:
            response = response.split("```")[1].replace("json", "").strip()
        return json.loads(response)
    except Exception:
        # Fallback safe defaults if the LLM fails to structure JSON
        if intent == "refund":
            return ["What is the specific reason for your refund request?"]
        return []