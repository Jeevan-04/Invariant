import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
from ai_execution_boundary.control.orchestrator import Invariant, Identity, ModelSpec, ContextSpec, ContextSource

# Load environment logic (keys should be in .env or system env)
load_dotenv()

st.set_page_config(page_title="Invariant Kernel", page_icon="🛡️", layout="wide")

# --- Sidebar: Kernel State ---
with st.sidebar:
    st.title("🛡️ Invariant")
    st.caption("Execution Kernel v1.0")
    
    # 1. API Key Injection
    api_key = st.text_input("API Key (OpenAI / OpenRouter)", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.divider()
    
    # 2. Active Policy
    st.subheader("Kernel Policy")
    st.info("📜 **Reality-Only Protocol**\n\nEnforced Constraints:\n- No Hypotheticals ('What if...')\n- No Imagination ('Imagine...')\n- No Fiction ('Write a story...')\n\n*The AI can only discuss what exists.*")
    st.caption("Note: Regex is used for demo transparency. The Kernel is logic-agnostic.")
    policy_option = "policies/reality_only.json"
    
    
    # 3. Model Logic (Simplified)
    # We always use OpenAI configuration. If key is missing, the adapter handles it gracefully.
    selected_model = "openai"
    
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
        
        # PERSISTENT KERNEL INTERNALS
        # If this message has attached kernel metadata, render it.
        # This ensures the "Proof" doesn't disappear when you scroll away.
        if "kernel_data" in message:
            kd = message["kernel_data"]
            proof_id = kd.get("proof_id", "N/A")
            receipt = kd.get("receipt", {})
            
            with st.expander(f"🔍 Kernel Receipt: {proof_id[:12]}...", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("Cryptographic Proof ID")
                    st.code(proof_id, language="text")
                with col2:
                    st.caption("Node Signature")
                    # Extract signature from saved receipt structure
                    try:
                        sig = receipt.get("integrity", {}).get("signatures", [{}])[0].get("signature", "N/A")
                    except:
                        sig = "N/A"
                    st.code(sig[:24] + "...", language="text")

                st.json(receipt)
                st.caption("Traceability: This JSON object allows full computational replay of this turn.")

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
                time.sleep(0.005) 
            
            # Final display with Approval Badge
            message_placeholder.markdown(
                f"""
                {display_text}
                
                ---
                <span style='color:green; font-size:0.8em'>
                ✅ <b>Invariant Kernel Approved</b> | Proof: `{proof_id[:8]}...`
                </span>
                """, 
                unsafe_allow_html=True
            )
            
            # Prepare Kernel Data for Persistence
            full_receipt = {
                "schema": "invariant.receipt.v1",
                "meta": {"proof_id": proof_id, "timestamp": "2026-01-04T..."},
                "graph": json.loads(result["graph"].to_json()),
                "integrity": result.get("integrity")
            }
            
            # Show Internals Immediately (and save them!)
            with st.expander(f"🔍 Kernel Receipt: {proof_id[:12]}...", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("Cryptographic Proof ID")
                    st.code(proof_id, language="text")
                with col2:
                    st.caption("Node Signature")
                    try:
                        sig = result.get("integrity", {}).get("signatures", [{}])[0].get("signature", "N/A")
                    except:
                        sig = "N/A"
                    st.code(sig[:24] + "...", language="text")
                st.json(full_receipt)
                
            # Update State with content AND kernel structure
            # This is the key fix: storing the complex object in history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"{output_text}\n\n*✅ Verified Proof: `{proof_id[:12]}...`*",
                "kernel_data": {
                    "proof_id": proof_id,
                    "receipt": full_receipt
                }
            })
            
            st.session_state.last_proof = proof_id
            status_indicator.markdown("🟢 **Verified**: Execution Sealed.")
            proof_display.code(proof_id)
            
        except Exception as e:
            # Policy Violation Handling
            error_msg = str(e)
            if "Policy Violation" in error_msg or "Abort" in error_msg:
                st.error(f"🚫 BLOCKED: {error_msg}")
                # Save the block event too!
                st.session_state.messages.append({"role": "assistant", "content": f"🚫 [BLOCKED] {error_msg}"})
                status_indicator.markdown("⛔ **Aborted**: Policy Violation.")
            else:
                st.error(f"System Error: {error_msg}")
                status_indicator.markdown("⚠️ **Error**")
