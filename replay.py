import sys
import json
import os
from ai_execution_boundary.control.orchestrator import execute, Invariant
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource

def replay_execution(record_path: str):
    print(f"\n\033[1;34m=== Invariant Replay Verification ===\033[0m")
    print(f"Loading Record: {record_path}")
    
    with open(record_path, "r") as f:
        receipt = json.load(f)
    
    # Schema Validation (V1)
    if receipt.get("schema") != "invariant.receipt.v1":
        # Fallback for legacy records or error
        print("\033[1;31m[WARNING] Unknown or missing schema version. Attempting legacy parse...\033[0m")
        # Legacy structure was flat meta/graph
        if "meta" in receipt and "graph" in receipt:
             meta = receipt["meta"]
             graph = receipt["graph"]
             stored_proof = meta["proof"]
        else:
             print("FAILURE: Invalid Receipt Format.")
             return False
    else:
        # V1 Parse
        meta = receipt["meta"]
        graph = receipt["graph"]
        stored_proof = meta["proof_id"] # V1 uses proof_id

    print(f"Recorded Proof: \033[1;33m{stored_proof}\033[0m")
    
    # Reconstruct Arguments from Graph JSON
    # 1. Identity
    identity = Identity(
        user_id=graph["identity"]["user_id"],
        role=graph["identity"]["role"],
        org=graph["identity"]["org"],
        env=graph["identity"]["env"]
    )
    
    # 2. ModelSpec
    m_data = graph["model"]
    model_spec = ModelSpec(
        provider=m_data["provider"],
        name=m_data["name"],
        version=m_data["version"],
        seed=m_data["seed"],
        decoding_strategy=m_data["decoding_strategy"],
        extra_params=m_data.get("extra_params", {})
    )
    
    # 3. ContextSpec
    # Note: We must NOT assume the hashes in the graph are the TRUTH on disk.
    # We load based on identifier, and the Orchestrator will RE-HASH the files on disk.
    # If the file on disk changed, the new hash will differ from the recorded graph hash.
    # This is exactly what we want to detect (Context Rot).
    
    sources = []
    for s_data in graph["context"]["sources"]:
        sources.append(ContextSource(
            type=s_data["type"],
            sensitivity=s_data["sensitivity"],
            identifier=s_data["identifier"]
            # We explicitly DO NOT copy content_hash from the record.
            # We want current execution to compute it fresh.
        ))
    context_spec = ContextSpec(sources)
    
    # 4. Inputs
    input_payload = graph["input_payload"]
    policy_name = graph["policy_name"] # Path or name
    
    print("\n[Replaying Execution...]")
    results = execute(
        input_payload=input_payload,
        identity=identity,
        model_spec=model_spec,
        context_spec=context_spec,
        policy_name=policy_name
    )
    
    new_proof = results["proof"]
    
    print(f"\n[Verification]")
    print(f"Recorded Proof: {stored_proof}")
    print(f"Replay Proof:   {new_proof}")
    
    if new_proof == stored_proof:
        print(f"\033[1;32m[SUCCESS] Proof Verified. Execution is reproducible.\033[0m")
        return True
    else:
        print(f"\033[1;31m[FAILURE] Proof Mismatch! The environment has drifted (policy, context, or code).\033[0m")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 replay.py <record.json>")
        sys.exit(1)
        
    success = replay_execution(sys.argv[1])
    sys.exit(0 if success else 1)
