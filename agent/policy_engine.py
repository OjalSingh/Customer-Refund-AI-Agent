import json
from llm import ask_llm

def evaluate_policy_compliance(policy_text, workflow, state_data):
    txns = state_data.get("transactions", [])
    compressed_txns = [{"merchant": t.get("merchant"), "amount": t.get("amount"), "status": t.get("status")} for t in txns]

    prompt = f"""[System: Compliance Auditor. Match Evidence against Policy Rules. Return ONLY raw JSON.]

Schema:
{{"eligible": true/false, "reasoning": ["brief reason 1", "brief reason 2"]}}

### RULES
{policy_text}

### EVIDENCE
Workflow: {workflow}
Intent: {state_data.get("intent")}
Merchant Asked: {state_data.get("merchant")}
Transactions: {json.dumps(compressed_txns)}

JSON:"""

    response = ask_llm(prompt).strip()
    try:
        if "```" in response:
            response = response.split("```")[1].replace("json", "").strip()
        return json.loads(response)
    except Exception:
        return {
            "eligible": False,
            "reasoning": ["Failed to safely compile LLM policy checks. Escalating."]
        }