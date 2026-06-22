# Deterministic Financial Operations AI Agent

A high-fidelity, state-driven customer operations AI agent designed for complex fintech workflows (Refunds, Fraud Analysis, Order Cancellations). This project demonstrates a decoupled architecture that separates unstructured natural language processing from rigid, compliance-grade business logic.

Built to run entirely locally using open-weight models via **Ollama (Qwen/Llama 3)**, but fully model-agnostic and built to scale to enterprise cloud infrastructures.

---

## 🏗️ Architectural Core Principles

### 1. Isolated State Management (`AgentState`)
Unlike standard conversational chatbots that pass entire transcripts back and forth, this agent uses a centralized, protected state object. The LLM is used strictly for **semantic extraction** (e.g., pulling intentions, values, and entities), while the final transactional routing and operations decision-making (`APPROVE`, `REJECT`, `ESCALATE`) are executed inside immutable code barriers. This eliminates transaction hallucinations completely.

### 2. Payload Optimization & Token Shaving
To combat latency and lower operational costs, the architecture compresses deep transaction arrays into lightweight string summaries *before* hitting the LLM reasoning blocks. This decreases context processing windows and lowers Time-to-First-Token (TTFT).

### 3. Dynamic Triage Auditing (No Rigid Menus)
Instead of forcing users through frustrating, legacy phone-tree IVR structures (*"Press 1 for Refunds"*), the triage module cross-checks static corporate text policies against what the user *has already stated*. It dynamically audits missing parameters on the fly and generates highly contextual follow-up questions *only* for the information it still needs.

---

## 🛠️ Tech Stack & Dependencies
* **Core Language:** Python 3.10+
* **Inference Engine:** Ollama (Targeting `qwen2.5:3b` / `llama3.1:8b`)
* **State Framework:** Event-Driven Context Registry
* **Data Storage:** Simulated local JSON schemas (`data/users.json`, `data/transactions.json`)

---

## 🚀 Live Execution Trace

Below is a live, verified execution run of the pipeline processing a complex double-billing case that triggers a defensive fraud escalation pathway:

```text
⚡ REASONING REFUND AGENT INTERFACE ⚡

Customer Message: I got charged twice by Netflix
DEBUG INTENT: fraud

--- Clarification Needed ---
Agent: What were the amounts of the two charges?
Customer: 15.49
Agent: Were both charges successful, or did one get refunded?
Customer: both successful
----------------------------

Agent: Please provide your User ID to pull transaction context: U001
==================================================
INVESTIGATION REPORT
==================================================

User ID: U001
Intent: fraud
Decision: ESCALATE
Risk Level: LOW
Risk Score: 0

Explanation:
1. Summary of what happened  
Two successful transactions (TXN101 and TXN102) were processed for user U001 to Netflix, each totaling $15.49, within 15 seconds of each other on June 20, 2026.  

2. Evidence considered  
- Transactions: Identical amounts, same merchant, and nearly simultaneous timestamps.  
- Risk Assessment: Low risk score (0) with no flagged reasons or signals.  
- Policy Check: No policy violations detected.  

3. Why decision was made  
While the risk and policy systems did not flag the transactions, the near-simultaneous, identical charges to the same merchant raise suspicion of potential fraud (e.g., account compromise, duplicate charges, or intentional testing). The lack of risk signals may indicate a false negative, warranting manual review to confirm legitimacy.  

4. Next step recommendation  
Verify with the user (U001) to confirm if the transactions were authorized. Cross-check with Netflix to validate the charges. Monitor for additional suspicious activity linked to this user or merchant.

Audit Trail:
- Agent started
- Intent extracted using Qwen
- Workflow selected: fraud
- Baseline financial risk assessed
- Fraud detected → Escalate to Risk Operations
- Structured explanation generated
- LLM conversation layer response created


```


# 📂 Project Structure
Bash
├── app.py                         # Runtime entry-point & UI loop
├── data/
│   ├── transactions.json          # Real-world mock customer ledgers
│   └── users.json                 # Premium, standard, and flagged profiles
├── agent/
│   ├── support_agent.py           # Core Orchestrator & routing state machine
│   ├── intent_extractor.py        # Semantic classification engine
│   ├── question_manager.py        # Dynamic text-policy information auditor
│   ├── explanation_generator.py   # State metadata aggregation
│   └── explanation_llm.py         # Customer-facing conversational synthesis
└── tools/
    └── policy_retriever.py        # Dynamic local policy lookups
🔧 Installation & Local Setup


# Clone the Repository

## Bash
git clone [https://github.com/your-username/deterministic-finops-agent.git](https://github.com/your-username/deterministic-finops-agent.git)
cd deterministic-finops-agent
Start your Local Inference Engine
Ensure Ollama is running on your machine, then pull the target lightweight model:

## Bash
ollama pull qwen2.5:3b
Run the Application

## Bash
python app.py