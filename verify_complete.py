import sys
import os
import hashlib
from ai_execution_boundary.control.orchestrator import execute
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource

# Setup Common Objects
identity = Identity("jeevan", "auditor", "invariant", "prod")
model_spec = ModelSpec("mock", "verify-model", "v1", 42, "greedy")

def print_header(msg):
    print(f"\n\033[1;34m=== {msg} ===\033[0m")

def print_pass(msg):
    print(f"\033[1;32m[PASS] {msg}\033[0m")

def test_policy_enforcement():
    print_header("Test 1: Policy Enforcement (Security)")
    
    # 1. Valid Input
    try:
        res = execute("Hello World", identity, model_spec, ContextSpec([]), policy_name="safety")
        print_pass("Valid input admitted.")
    except Exception as e:
        print(f"FAILURE: Valid input rejected: {e}")
        sys.exit(1)

    # 2. Malicious Input (Case Insensitive)
    try:
        execute("Please DrOp TaBlE users", identity, model_spec, ContextSpec([]), policy_name="safety")
        print("FAILURE: Malicious input was NOT rejected!")
        sys.exit(1)
    except Exception as e:
        if "Policy Violation" in str(e) or "Aborted" in str(e):
            print_pass(f"Malicious input blocked: {e}")
        else:
            print(f"WARNING: Rejected but with unexpected error: {e}")

def test_context_attribution():
    print_header("Test 2: Context Attribution (Causality)")
    
    # Create temp context
    with open("ctx_A.txt", "w") as f: f.write("Data A")
    
    ctx = ContextSpec([ContextSource("file", "internal", "ctx_A.txt")])
    res1 = execute("Query", identity, model_spec, ctx, "safety")
    
    # Modify context
    with open("ctx_A.txt", "w") as f: f.write("Data B") # Changed content
    
    res2 = execute("Query", identity, model_spec, ctx, "safety")
    
    if res1['proof'] == res2['proof']:
        print("FAILURE: Proofs identical despite context change!")
        sys.exit(1)
    else:
        print_pass("Proofs diverged on context modification.")
    
    # Cleanup
    if os.path.exists("ctx_A.txt"): os.remove("ctx_A.txt")

def test_canonical_ordering():
    print_header("Test 3: Canonical Ordering (Determinism)")
    
    # Create two context files
    with open("file_1.txt", "w") as f: f.write("Content 1")
    with open("file_2.txt", "w") as f: f.write("Content 2")
    
    # Order A: [1, 2]
    ctx_order_a = ContextSpec([
        ContextSource("file", "internal", "file_1.txt"),
        ContextSource("file", "internal", "file_2.txt")
    ])
    
    # Order B: [2, 1] (Swapped)
    ctx_order_b = ContextSpec([
        ContextSource("file", "internal", "file_2.txt"),
        ContextSource("file", "internal", "file_1.txt")
    ])
    
    print("Executing Order A...")
    res_a = execute("Query", identity, model_spec, ctx_order_a, "safety")
    
    print("Executing Order B...")
    res_b = execute("Query", identity, model_spec, ctx_order_b, "safety")
    
    if res_a['proof'] == res_b['proof']:
        print_pass(f"Canonical Sort verified! Proofs match: {res_a['proof']}")
    else:
        print(f"FAILURE: Order changed proof! Sort not working.\nA: {res_a['proof']}\nB: {res_b['proof']}")
        sys.exit(1)

    # Cleanup
    if os.path.exists("file_1.txt"): os.remove("file_1.txt")
    if os.path.exists("file_2.txt"): os.remove("file_2.txt")

if __name__ == "__main__":
    test_policy_enforcement()
    test_context_attribution()
    test_canonical_ordering()
