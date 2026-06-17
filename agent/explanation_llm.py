from llm import ask_llm

def generate_explanation(state):

    prompt = f"""
You are a support investigation analyst.

Use ONLY the provided state.

INTENT:
{state.value("intent")}

TRANSACTIONS:
{state.value("transactions")}

POLICY RESULT:
{state.value("policy_result")}

RISK RESULT:
{state.value("risk_result")}

DECISION:
{state.value("decision")}

Write a professional explanation:

1. Summary of what happened
2. Evidence considered
3. Why decision was made
4. Next step recommendation

Rules:
- Do NOT invent facts
- Only use provided data
- Be concise and professional
"""

    return ask_llm(prompt)