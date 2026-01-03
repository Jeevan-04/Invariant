from ai_execution_boundary.control.orchestrator import execute, Invariant, Identity, ModelSpec, ContextSpec, ContextSource

# Setup
identity = Identity("jeevan", "auditor", "invariant", "demo")
model = ModelSpec("mock", "demo-model", "v1", 42, "greedy")

# Create a persistent context file
ctx_file = "demo_ctx.txt"
with open(ctx_file, "w") as f: 
    f.write("This is the immutable knowledge base for the demo.")

context = ContextSpec([ContextSource("file", "internal", ctx_file)])

print("--- Running Demo Execution ---")
# Execute
inv = Invariant()
res = execute("Explain Invariant", identity, model, context, policy_name="safety")

# Save Receipt
receipt_path = "demo_receipt.json"
inv.save_record(res, receipt_path)

print(f"\n[SUCCESS] Receipt saved to: {receipt_path}")
print(f"Context saved to: {ctx_file}")
print("\nNow you can run:")
print(f"  python3 replay.py {receipt_path}")
print(f"  echo 'Modification' >> {ctx_file} && python3 replay.py {receipt_path}")
