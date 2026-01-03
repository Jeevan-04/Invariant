from ai_execution_boundary.control.orchestrator import execute
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource
import os
import sys

def test_context_attribution():
    print("\n=== Verifying Phase 4: Multi-Context Attribution ===")
    
    # Setup Identity and Model
    identity = Identity("jeevan", "tester", "invariant", "verify_context")
    model = ModelSpec("mock", "context-test-model", "v1", 42, "greedy")

    # Setup Context File
    ctx_filename = "temp_context.txt"
    with open(ctx_filename, "w") as f:
        f.write("Version 1: Trusted Knowledge")
    
    context_v1 = ContextSpec([ContextSource("file", "internal", ctx_filename)])
    
    print("\n[Test 1] Execution with Context Version 1")
    try:
        res1 = execute("Summarize this", identity, model, context_v1, policy_name="safety")
        proof1 = res1['proof']
        print(f"Proof V1: {proof1}")
    except Exception as e:
        print(f"FAILURE: Execution V1 failed: {e}")
        sys.exit(1)

    # Modify Context
    print("\n[Test 2] Modifying Context File...")
    with open(ctx_filename, "w") as f:
        f.write("Version 2: Malicious Injection Attempt") # Different content
    
    # Re-run
    print("[Test 3] Execution with Context Version 2")
    try:
        res2 = execute("Summarize this", identity, model, context_v1, policy_name="safety")
        proof2 = res2['proof']
        print(f"Proof V2: {proof2}")
    except Exception as e:
        print(f"FAILURE: Execution V2 failed: {e}")
        sys.exit(1)
        
    # Verification
    print("\n[Verification]")
    if proof1 == proof2:
        print("FAILURE: Proofs are IDENTICAL despite context change! Attribution failed.")
        sys.exit(1)
    else:
        print("SUCCESS: Proofs Diverged. Context change was cryptographically bound.")
        print(f"Delta: {proof1} != {proof2}")

    # Cleanup
    if os.path.exists(ctx_filename):
        os.remove(ctx_filename)

if __name__ == "__main__":
    test_context_attribution()
