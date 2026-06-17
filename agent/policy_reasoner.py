from llm import ask_llm


def generate_explanation(
    document_contents,
    transactions,
    policy_result,
    risk_result,
    decision
):

    prompt = f"""
You are a support investigation analyst.

Use ONLY the evidence provided.

DOCUMENTS:
{document_contents}

TRANSACTIONS:
{transactions}

POLICY RESULT:
{policy_result}

RISK RESULT:
{risk_result}

FINAL DECISION:
{decision}

Write a professional investigation report containing:

1. Investigation Summary
2. Evidence Found
3. Policy Evaluation
4. Risk Assessment
5. Final Decision
6. Recommended Next Step

Rules:
- Use only supplied evidence.
- Do not invent facts.
- If the request is not eligible, explain why.
- If the request is escalated, explain why.
- Mention the final decision exactly as provided.

Return plain text only.
"""

    return "Explanation generation skipped."