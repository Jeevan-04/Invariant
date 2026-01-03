from ai_execution_boundary.control.orchestrator import execute
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource
import os
import sys

def test_policy_enforcement():
    print("\n=== Verifying Phase 3: Policy Enforcement ===")
    
    identity = Identity("jeevan", "tester", "invariant", "verify_policy")
    context = ContextSpec([ContextSource("static", "test", "verification")])
    model = ModelSpec("mock", "policy-test-model", "v1", 42, "greedy") # Mock is fine, we test precheck
    
    # Test 1: Admissible Input
    print("\n[Test 1] Admissible Input: 'Hello World'")
    try:
        result = execute("Hello World", identity, model, context, policy_name="safety")
        print("SUCCESS: Input Admitted. Proof:", result['proof'])
    except Exception as e:
        print("FAILURE: Admissible input was rejected:", e)
        sys.exit(1)

    # Test 2: Inadmissible Input (SQL Injection)
    print("\n[Test 2] Inadmissible Input: 'Please DROP TABLE users'")
    try:
        execute("Please DROP TABLE users", identity, model, context, policy_name="safety")
        print("FAILURE: Malicious input was NOT rejected!")
        sys.exit(1)
    except Exception as e:
        if "Policy Violation" in str(e) or "Aborted" in str(e):
             print(f"SUCCESS: Malicious input rejected as expected. Error: {e}")
        else:
             print(f"WARNING: Rejected but with unexpected error: {e}")

    # Test 3: Mixed Case Input
    print("\n[Test 3] Mixed Case Input: 'Please DrOp TaBlE users'")
    try:
        execute("Please DrOp TaBlE users", identity, model, context, policy_name="safety")
        print("FAILURE: Mixed-case malicious input was NOT rejected!")
        sys.exit(1)
    except Exception as e:
        if "Policy Violation" in str(e) or "Aborted" in str(e):
             print(f"SUCCESS: Mixed-case input rejected as expected. Error: {e}")
        else:
             print(f"WARNING: Rejected but with unexpected error: {e}")
             # We assume C++ throws runtime_error which pybind converts
             
if __name__ == "__main__":
    test_policy_enforcement()
