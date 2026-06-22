from llm import ask_llm
import json

def evaluate_refund_with_policy(policy_text, intent, transactions, context):
    prompt = f"""
You are a Refund Policy Enforcement Engine.
Analyze the following policy rules against the customer's situation.

--- POLICY RULES ---
{policy_text}

--- CASE DETAILS ---
Intent: {intent}
Customer Context: {context}
Transactions: {json.dumps(transactions)}

Determine if the request is eligible under the rules.
Return ONLY a valid JSON object with keys "eligible" (boolean) and "reasoning" (list of strings).
"""
    response = ask_llm(prompt)
    try:
        return json.loads(response)
    except Exception:
        return {"eligible": False, "reasoning": ["Failed to parse policy evaluation."]}