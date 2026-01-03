from ai_execution_boundary.control.orchestrator import execute
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource

def verify_setup():
    print("--- Verifying Invariant Setup ---")
    
    # Define Identity
    identity = Identity("jeevan", "Creator", "invariant", "dev")
    
    # Define Model Spec (Using Mock Adapter)
    model = ModelSpec("mock", "test-model", "v0", 12345, "greedy")
    
    # Define Context
    context = ContextSpec([ContextSource("static", "public", "init_test")])
    
    # Execute
    print("\n[Action] Requesting Execution...")
    try:
        result = execute(
            input_payload="Status Check",
            identity=identity,
            model_spec=model,
            context_spec=context,
            policy_name="system_init_policy"
        )
        print("\n[Result] Execution SUCCESS")
        print(f"Output: {result['output']}")
        print(f"Proof: {result['proof']}")
        
        if "PROOF" not in str(result['proof']).upper() and "mock_proof" not in str(result['proof']):
             print("WARNING: Proof format looks unexpected.")
             
    except Exception as e:
        print(f"\n[Result] Execution FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    verify_setup()
