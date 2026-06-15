import json
from llm import ask_llm


def extract_intent(message):

    prompt = f"""
You are an information extraction system.

Return ONLY valid JSON.

Schema:
{{
    "intent": "",
    "merchant": ""
}}

Message:
{message}
"""

    response = ask_llm(prompt)

    return json.loads(response)