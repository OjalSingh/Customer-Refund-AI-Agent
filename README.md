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
```text
Bash
├───app.py                      # Main interface & interactive application loop
├───llm.py                      # Local LLM connector framework (Ollama abstraction)
├───README.md                   # System documentation
├───requirements.txt            # Project dependencies
│   
├───agent                       # Agentic Core Orchestration Layer
│   ├── executor.py             # Event loop & state execution engine
│   ├── explanation_generator.py # Structured metadata extraction & alignment
│   ├── explanation_llm.py      # Conversational customer text synthesis
│   ├── intent_extractor.py     # Semantic input classification
│   ├── intent_node.py          # Node routing registry for state trees
│   ├── policy_engine.py        # Programmatic compliance checking logic
│   ├── question_manager.py     # Dynamic missing-variable triage auditor
│   ├── report_generator.py     # Analytical terminal summary compiling
│   ├── router.py               # Algorithmic intent-to-workflow router
│   ├── state.py                # Thread-safe unified transaction state tracking
│   ├── support_agent.py        # Pipeline execution & workflow manager
│   ├── tool_registry.py        # Tool-to-agent binding gateway
│   └──_init_.py
│       
├───data                        # Mock Enterprise Datastores
│   ├── transactions.json       # Live client transaction history records
│   └── users.json              # Structured account access profiles
│       
├───guardrails                  # Security & Compliance Boundaries
│   └──validation.py           # Explicit logic filters blocking structural leakage
│       
├───policies                    # Core Corporate Guideline Datastores
│   ├──fraud_policy.txt        # Text requirements for velocity checks
│   ├──refund_policy.py        # Programmatic execution mirrors for refunds
│   ├──refund_policy.txt       # Hard criteria documentation for billing errors
│   └──subscription_policy.txt # Scope rules for recurring account cancellations
│       
├───risk                        # Safety & Assessment Services
│   └──risk_engine.py          # Multi-factor score calculator & fraud engine
│       
└───tools                       # High-Fidelity Data Extraction & Utility APIs
    ├──document_loader.py      # Local file data normalization
    ├──document_retriever.py   # Semantic document retrieval engine
    ├──duplicate_detector.py   # Chronological transaction stream evaluation
    ├──investigation_engine.py # Core transaction audit processing system
    ├──policy_retriever.py     # Live text-policy context manager
    ├──transaction_tool.py     # Target transaction fetching wrapper
    ├──user_tool.py            # User profile data parser
    └──__init_.py


```

# 🔧 Installation & Local Setup
## Clone the Repository

### Bash
git clone [https://github.com/your-username/deterministic-finops-agent.git](https://github.com/your-username/deterministic-finops-agent.git)
cd deterministic-finops-agent
Start your Local Inference Engine
Ensure Ollama is running on your machine, then pull the target lightweight model:

### Bash
ollama pull qwen2.5:3b
Run the Application

### Bash
python app.py