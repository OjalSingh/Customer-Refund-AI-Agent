import streamlit as st
from agent.support_agent import run_agent

# 1. Page Configuration & Aesthetic Layout
st.set_page_config(page_title="FinOps Agent Framework", page_icon="🛡️", layout="wide")

st.title("🛡️ Autonomous FinOps & Risk Agent Engine")
st.markdown("A local, guardrailed state-machine agent executing semantic policy compliance via local vector embeddings (`all-minilm`).")
st.markdown("---")

# 2. Side Panel Configuration (Displays current State Machine Variables)
with st.sidebar:
    st.header("⚙️ Engine Parameters")
    user_id = st.text_input("Simulated User ID", value="U001")
    st.markdown("---")
    st.subheader("📚 Loaded RAG Repositories")
    st.caption("• policies/refund_policy.txt")
    st.caption("• policies/fraud_policy.txt")
    st.caption("• policies/subscription_policy.txt")

# Initialize Chat Memory State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Conversational History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Dynamic User Interaction Flow
if user_input := st.chat_input("Enter transaction query (e.g., 'I got charged twice by Netflix')"):
    
    # Render user prompt immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Trigger Backend Orchestrator Stream
    with st.spinner("Executing agentic state-machine iteration loops..."):
        # Run your actual backend code!
        agent_final_state = run_agent(user_message=user_input, user_id=user_id)
        
        # Pull generated components out of your AgentState dictionary
        llm_response = agent_final_state.get("explanation", "No response generated.")
        decision = agent_final_state.get("decision", "REJECT")
        retrieved_policy = agent_final_state.get("policy", "No policy matches found.")

    # Render Agent Response
    with st.chat_message("assistant"):
        # Visual badge highlighting the isolated state machine decision output
        if decision == "ESCALATE":
            st.error(f"🚨 SYSTEM STATE: [ESCALATE TO RISK OPERATIONS]")
        elif decision == "REJECT":
            st.warning(f"⚠️ SYSTEM STATE: [REJECT TRANSACTION]")
        else:
            st.success(f"✅ SYSTEM STATE: [{decision}]")
            
        st.markdown(llm_response)
        
        # Collapsible section proving your RAG system worked beautifully
        with st.expander("🔍 System Audit Trail (Semantic RAG Chunks Used)"):
            st.code(retrieved_policy, language="text")

    st.session_state.messages.append({"role": "assistant", "content": llm_response})