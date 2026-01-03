import os
import sys
from ai_execution_boundary.control.orchestrator import execute
from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ContextSource

# Helper to print colored output if supported, else plain
def print_header(msg):
    print(f"\n\033[1;34m=== {msg} ===\033[0m")

def print_success(msg):
    print(f"\033[1;32m[PASS] {msg}\033[0m")

def print_info(msg):
    print(f"\033[1;36m[INFO] {msg}\033[0m")

def print_proof(hash_str):
    print(f"\033[1;33m[PROOF] {hash_str}\033[0m")

def main():
    print_header("Invariant: Execution Boundary CLI")
    print("Type 'exit' to quit.")
    
    # Default Identity
    identity = Identity("jeevan", "tester", "invariant", "cli")
    
    # Default Context
    context = ContextSpec([ContextSource("static", "cli", "user_input")])
    
    while True:
        try:
            print("\n------------------------------------------------")
            user_input = input("Enter Prompt > ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Allow user to toggle live model if key exists
            use_live = os.environ.get("OPENAI_API_KEY") is not None
            if use_live:
                print_info("Using Live Model (OpenRouter/OpenAI)")
                model = ModelSpec(
                    provider="openai",
                    name="google/gemini-2.0-flash-exp:free",
                    version="latest",
                    seed=42,
                    decoding_strategy="temperature=0.7",
                    extra_params={"base_url": "https://openrouter.ai/api/v1"}
                )
            else:
                print_info("Using Mock Model (Set OPENAI_API_KEY to switch to live)")
                model = ModelSpec("mock", "cli-model", "v1", 42, "greedy")

            print_info("Requesting Execution...")
            
            result = execute(
                input_payload=user_input,
                identity=identity,
                model_spec=model,
                context_spec=context,
                policy_name="safety"
            )
            
            print_success("Execution Admitted & Sealed")
            print(f"Output: {result['output']}")
            print_proof(result['proof'])
            
        except Exception as e:
            print(f"\033[1;31m[ERROR] {e}\033[0m")

if __name__ == "__main__":
    # Ensure dependencies are loaded
    # On first run, it might need the virtualenv source, but user is in terminal
    main()
