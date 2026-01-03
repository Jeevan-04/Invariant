import sys
from ai_execution_boundary.control.orchestrator import execute, Invariant, Identity, ModelSpec, ContextSpec, ContextSource

def test_active_kernel():
    print("\n=== Verifying Phase 10: Active Kernel Logic ===")
    
    # Setup
    identity = Identity("jeevan", "tester", "invariant", "active-test")
    model = ModelSpec("mock", "stream-test", "v1", 40, "greedy") # Seed 40 % 5 = 0 -> "This is a deterministic response A."
    context = ContextSpec([]) # No context needed
    
    # Run Orchestrator
    try:
        print("[Step 1] Executing with Policy: Block 'response'")
        inv = Invariant()
        res = inv.execute(
            input_payload="Generate Text",
            identity=identity,
            model_spec=model,
            context_spec=context,
            policy_name="policies/verify_stream.json"
        )
        print("\n[FAILURE] Execution Completed! It should have been Aborted.")
        print(f"Output: {res['output']}")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[SUCCESS] Caught Expected Exception: {e}")
        if "Policy Violation Mid-Stream" in str(e) or "Policy Violation" in str(e):
            print("Verified: Kernel blocked execution mid-stream.")
        else:
            print(f"[WARNING] Exception message diff from expected: {e}")

if __name__ == "__main__":
    test_active_kernel()
