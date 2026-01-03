import os
from ai_execution_boundary.control.orchestrator import execute
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource

def verify_openrouter():
    print("--- Verifying Invariant with OpenRouter ---")
    
    identity = Identity("jeevan", "Creator", "invariant", "prod")
    
    # We use a cheap model on OpenRouter for testing
    model = ModelSpec(
        provider="openai", 
        name="google/gemini-2.0-flash-exp:free", 
        version="latest", 
        seed=42, 
        decoding_strategy="temperature=0.7",
        extra_params={
            "base_url": "https://openrouter.ai/api/v1",
            # We will pass the key via env var for safety in real apps, 
            # but for this script we assume it's set in the environment running this.
        }
    )
    
    context = ContextSpec([ContextSource("static", "public", "openrouter_test")])
    
    print("\n[Invariant] Requesting Execution from OpenRouter...")
    try:
        result = execute(
            input_payload="Explain the concept of an 'Invariant' in computer science in one sentence.",
            identity=identity,
            model_spec=model,
            context_spec=context,
            policy_name="live_test_policy"
        )
        print("\n[Result] Execution SUCCESS")
        print(f"Output: {result['output']}")
        print(f"Proof: {result['proof']}")
             
    except Exception as e:
        print(f"\n[Result] Execution FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    verify_openrouter()
