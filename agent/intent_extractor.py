import json
from llm import ask_llm

def extract_intent(message):
    prompt = f"""[System: JSON Extraction Engine. Return ONLY valid JSON matching the schema. No conversational prose.]

Schema:
{{"intent": "refund" / "fraud" / "subscription" / "order_cancellation" / "unknown", "merchant": "name or null"}}

Input Message:
"{message}"

JSON:"""

    response = ask_llm(prompt).strip()

    try:
        # Simple cleanup helper to strip accidental markdown wrappers like ```json
        if "```" in response:
            response = response.split("```")[1].replace("json", "").strip()
        return json.loads(response)
    except Exception:
        return {
            "intent": "unknown",
            "merchant": None
        }