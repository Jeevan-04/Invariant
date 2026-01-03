import streamlit as st
import os
import time
from dotenv import load_dotenv
from ai_execution_boundary.control.orchestrator import Invariant, Identity, ModelSpec, ContextSpec, ContextSource

# Load environment logic (keys should be in .env or system env)
load_dotenv()

st.set_page_config(page_title="Invariant Kernel", page_icon="🛡️", layout="wide")

# --- Sidebar: Kernel State ---
with st.sidebar:
    st.title("🛡️ Invariant Kernel")
    st.caption("Causality-Bound Execution Engine")
    
    st.subheader("Configuration")
    policy_option = st.selectbox(
        "Active Policy",
        ["policies/safety.json", "policies/india_only.json"],
        index=1 # Default to Patriot Policy
    )
    
    selected_model = st.selectbox(
        "Model Adapter",
        ["mock", "openai"],
        index=0 # Default to Mock for stability unless user has keys
    )
    
    st.divider()
    
    st.subheader("Live Verification")
    status_indicator = st.empty()
    proof_display = st.empty()
    
    if "last_proof" in st.session_state:
        st.success(f"Last Proof Sealed:\n{st.session_state.last_proof[:12]}...")
        with st.expander("View Receipt Details"):
            st.json(st.session_state.get("last_receipt_meta", {}))

# --- Main Interface ---
st.title("Invariant Chat")
st.markdown(
    """
    **Status**: `Enforce Mode`. Every token is inspected by the C++ boundary.
    Try asking about restricted topics (e.g., other countries) to test the *Patriot Policy*.
    """
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "invariant" not in st.session_state:
    st.session_state.invariant = Invariant()

# Setup Identity & Context
identity = Identity("user_guest", "tester", "public", "streamlit")
# Dynamic Context (could be file based)
ctx_file = "demo_ctx.txt"
if not os.path.exists(ctx_file):
    with open(ctx_file, "w") as f: f.write("Invariant Demo Knowledge Base.")
context = ContextSpec([ContextSource("file", "internal", ctx_file)])


# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Input
if prompt := st.chat_input("Enter your message..."):
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Assistant Response (Kernel Mediated)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_indicator.markdown("🔴 **Kernel Active**: Inspecting tokens...")
        
        try:
            # Prepare Spec
            model_spec = ModelSpec(selected_model, "chat-model", "v1", 42, "greedy")
            
            # EXECUTE (This runs the C++ Boundary Loop)
            # Note: This simulates streaming in the backend, but app.py waits for the result
            # because our current orchestrator returns the full sealed object, not a generator.
            result = st.session_state.invariant.execute(
                prompt, 
                identity, 
                model_spec, 
                context, 
                policy_name=policy_option
            )
            
            output_text = result["output"]
            proof_id = result["proof"]
            
            # Simulate streaming effect for UI polish
            display_text = ""
            for char in output_text:
                display_text += char
                message_placeholder.markdown(display_text + "▌")
                time.sleep(0.01) # Cosmetic typing effect
            message_placeholder.markdown(display_text)
            
            # Update State
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            st.session_state.last_proof = proof_id
            st.session_state.last_receipt_meta = {
                "timestamp": result.get("timestamp", "now"), # simplified
                "policy": policy_option,
                "proof": proof_id
            }
            status_indicator.markdown("🟢 **Verified**: Execution Sealed.")
            proof_display.code(proof_id)
            
        except Exception as e:
            # This catches the "Policy Violation Mid-Stream" error from orchestrator
            error_msg = str(e)
            if "Policy Violation" in error_msg or "Abort" in error_msg:
                st.error(f"🚫 BLOCKED: {error_msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"🚫 [BLOCKED] {error_msg}"})
                status_indicator.markdown("⛔ **Aborted**: Policy Violation.")
            else:
                st.error(f"System Error: {error_msg}")
                status_indicator.markdown("⚠️ **Error**")
