import sys
import os
from ai_execution_boundary.control.orchestrator import execute, Invariant, Identity, ModelSpec, ContextSpec, ContextSource
from replay import replay_execution

def test_replayability():
    print("\n=== Verifying Phase 6: Replayability ===")
    
    # Setup
    identity = Identity("jeevan", "auditor", "invariant", "replay-test")
    model = ModelSpec("mock", "replay-model", "v1", 42, "greedy")
    
    # Create a stable context file
    ctx_file = "replay_ctx.txt"
    with open(ctx_file, "w") as f: f.write("Stable Knowledge Base")
    
    context = ContextSpec([ContextSource("file", "internal", ctx_file)])
    
    # 1. Execute & Record
    print("\n[Step 1] Initial Execution & Recording")
    inv = Invariant() # Use instance to access save_record
    
    # Execute normal flow
    res = execute("Verify Me", identity, model, context, policy_name="safety")
    proof_original = res["proof"]
    
    record_path = "replay_receipt.json"
    inv.save_record(res, record_path)
    
    # 2. Replay Verification (Immediate)
    print("\n[Step 2] Immediate Replay Verification")
    success = replay_execution(record_path)
    if not success:
        print("FAILURE: Immediate replay failed.")
        sys.exit(1)

    # 3. Drift Detection Test
    print("\n[Step 3] Testing Context Drift Detection")
    # Determine the context ROT
    with open(ctx_file, "w") as f: f.write("Rotten Knowledge Base")
    
    print("Context file modified on disk. Replaying...")
    success_rot = replay_execution(record_path)
    
    if success_rot:
        print("FAILURE: Replay SUCCEEDED despite context rot! Hashing is broken.")
        sys.exit(1)
    else:
        print("SUCCESS: Replay correctly failed due to context drift.")

    # Cleanup
    if os.path.exists(ctx_file): os.remove(ctx_file)
    if os.path.exists(record_path): os.remove(record_path)

if __name__ == "__main__":
    test_replayability()
