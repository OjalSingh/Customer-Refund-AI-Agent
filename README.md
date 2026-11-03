# Deterministic Financial Operations AI Agent

A high-fidelity, state-driven customer operations AI agent designed for complex fintech workflows (Refunds, Fraud Analysis, Order Cancellations). This project demonstrates a decoupled architecture that separates unstructured natural language processing from rigid, compliance-grade business logic.

Built to run entirely on-prem using open-weight models via **Ollama (Qwen/Llama 3)**: no customer data has to leave the bank. The model only reads the request; a deterministic policy engine makes every decision and cites the policy clause it applied.

[![CI](https://github.com/OjalSingh/Customer-Refund-AI-Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/OjalSingh/Customer-Refund-AI-Agent/actions/workflows/ci.yml)

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
* **Inference Engine:** Ollama (`qwen3:8b`) by default; Claude Haiku or any OpenAI-compatible API optional
* **State Framework:** Event-Driven Context Registry
* **Data Storage:** Simulated local JSON schemas (`data/users.json`, `data/transactions.json`)

---

## ✅ Evaluation

`evals/cases.jsonl` holds 79 scripted customer requests across refunds, duplicate billing, fraud, subscription and order cancellations, account locks, clarification and 17 prompt-injection attempts, plus benign messages that only look like injections. A case passes when the agent returns the expected decision **and** cites the expected policy clause.

```bash
python -m evals.run_evals                        # with your configured model (default: Ollama)
LLM_PROVIDER=offline python -m evals.run_evals   # no model: keyword intent baseline, runs in CI
```

CI runs the offline baseline on every push and pull request and fails if the pass rate drops below 90% or if the agent approves anything it should not.

### Eval results: provider `offline`, model `default`

| Metric | Value |
| --- | --- |
| Cases | 79 |
| Pass rate (decision and cited clause) | 93.7% |
| Decision accuracy | 96.2% |
| Intent accuracy | 95.2% |
| Prompt-injection detection rate | 88.2% |
| Injection false-positive rate | 0.0% |
| Unsafe approvals | 0 |
| Avg seconds per case | 0.001 |

| Category | Cases | Pass rate |
| --- | --- | --- |
| account | 8 | 100.0% |
| benign | 4 | 100.0% |
| cancellation | 14 | 100.0% |
| clarification | 5 | 100.0% |
| duplicate | 6 | 66.7% |
| fraud | 10 | 100.0% |
| injection | 17 | 88.2% |
| refund | 15 | 93.3% |

Notes on reading these numbers:
- The offline baseline replaces the LLM with keyword intent extraction, so it is a floor, not the model's score. Its keyword lists were written alongside these cases, so treat it as a regression check. Run the suite with your model for the real number.
- **Unsafe approvals** counts cases where the agent approved something the policy does not allow. It stays at 0 even when an injection slips past the detector, because the model never decides: a missed injection can only change which clause is cited, not unlock an approval.

## 🔌 Model providers

The agent runs fully on-prem by default. A hosted model is an option for a public demo, not a requirement. Pick one with environment variables (see `.env.example`):

| `LLM_PROVIDER` | Model | Data leaves the machine? | Notes |
| --- | --- | --- | --- |
| `ollama` (default) | `qwen3:8b` | No | Needs a running Ollama |
| `anthropic` | `claude-haiku-5-5` | Yes | `pip install ".[hosted]"`, set `ANTHROPIC_API_KEY` |
| `openai` | set `LLM_MODEL` | Yes | Any OpenAI-compatible endpoint: Gemini (default `OPENAI_BASE_URL`), Groq, vLLM, LM Studio |
| `offline` | none | No | Keyword intent and template explanations; used by CI |

Whichever provider you choose, the decision comes from the same policy engine. Every run returns `state["llm_usage"]` with the tokens and estimated cost of each model call, and the eval report shows average tokens and total cost per run, so you can compare providers on the same 79 cases:

```bash
LLM_PROVIDER=anthropic python -m evals.run_evals --markdown evals/results/haiku.md
LLM_PROVIDER=ollama    python -m evals.run_evals --markdown evals/results/qwen.md
```

## ⚖️ How a decision is made

1. **Injection screen** (`guardrails/injection.py`): the raw message, and any follow-up answers, are checked before any model sees them. A match forces `REJECT` under `PROMPT-INJECTION-DEFENSE-GUARD` and the LLM is skipped.
2. **Intent extraction** (`agent/intent_extractor.py`): the LLM returns `{intent, merchant}` as JSON, validated with Pydantic. Invalid output, or no model, falls back to keyword rules. Merchants are only accepted if they exist in the ledger.
3. **Policy engine** (`agent/policy_engine.py`): plain Python applies the rules from `policies/*.txt` in priority order (account status, velocity attack, high value, duplicate charge, refund matrix, cancellation rules) and returns the decision, the clause id and the transactions it relied on.
4. **Explanation** (`agent/explanation_llm.py`): the LLM explains the decision it was given. It cannot change it.

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


# 🏛️ System Architecture & Data Flow Diagram
The following diagram illustrates how a user message dynamically orchestrates context aggregation, triggers local semantic array vector scoring, and passes bounded guardrail metrics to the execution layer.
```text
[ User Prompt Input via Streamlit UI ]
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │ 1. Intent Routing Node   │ ──> Categorizes (Refund / Fraud / Sub)
                      └─────────────┬────────────┘
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │ 2. Data Enrichment Hooks │ ──> Pulls Local User Ledger & History
                      └─────────────┬────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 3. Semantic Vector Search Layer (Local RAG)              │
       │                                                          │
       │    User Message                                          │
       │         │                                                │
       │         ▼                                                │
       │   [all-minilm] ──> Math Cosine Match ──> Memory Cache    │
       │                             │              ▲             │
       │                             ▼              │             │
       │                     [Top 2 Policy Chunks] ─┘             │
       └─────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │ 4. Prompt Synthesis      │ ──> Combines Context + Isolated Rules
                      └─────────────┬────────────┘
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │ 5. LLM Evaluation Engine │ ──> Enforces JSON Policy Ruleset Matrix
                      └─────────────┬────────────┘
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │ 6. Core State Guardrails │ ──> Hard Block / Escalate Determinations
                      └─────────────┬────────────┘
                                    │
                                    ▼
               [ Outbound State: ESCALATE / REJECT / APPROVE ]
               [ UI Render: Collapsible System Audit Trail   ]

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
git clone [https://github.com/your-username/deterministic-finops-agent.git]([https://github.com/OjalSingh/Customer-Refund-AI-Agent])
cd Customer-Refund-AI-Agent
Start your Local Inference Engine

## Environment Setup & Dependency Installation
Isolate your workspace and install the lightweight system requirements:
### Create a virtual environment
python -m venv venv
### Activate the environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
### Activate the environment (Mac/Linux)
source venv/bin/activate
### Install exact pinned dependencies
pip install -r requirements.txt

## Configure Local Embeddings & Models via Ollama
The semantic retrieval layers run locally to ensure 0% external cloud data leakage. Ensure Ollama is running on your machine, then pull the lightweight embedding model
### Bash
ollama pull qwen3:8b
ollama pull all-minilm

## Running the tests

```bash
uv sync                        # or: pip install -r requirements.txt pytest ruff
uv run ruff check .
uv run pytest
```

## Launching the Interactive Web UI Interface

### Bash
python -m streamlit run app.py
