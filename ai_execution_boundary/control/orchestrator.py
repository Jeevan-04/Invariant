import os
import sys
import hashlib
from typing import Optional, Dict, Any, Iterator
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Adjust path to find the control module if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ExecutionGraph, ContextSource
from ai_execution_boundary.models.adapters.base import ModelAdapter
# from ai_execution_boundary.models.adapters.openai import OpenAIAdapter # Lazy import
from ai_execution_boundary.models.adapters.mock import MockAdapter

# Try to import the C++ extension, fallback to mock if not built yet (for dev iteration)
try:
    import invariant_enforcement as enforcement
    print("[Invariant] C++ Enforcement Plane Loaded.")
except ImportError:
    print("[Invariant] WARNING: C++ Extension not found. Using Mock Boundary (INSECURE).")
    class MockBoundary:
        def load_policy(self, name): pass
        def load_model(self, spec): pass
        def load_context(self, ctx): pass
        def precheck(self, input): return True
        def run(self, input): return "MOCKED OUTPUT"
        def seal(self): return "mock_proof"
    enforcement = type('module', (), {'ExecutionBoundary': MockBoundary})

class Invariant:
    def __init__(self):
        self.boundary = enforcement.ExecutionBoundary()
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        print(f"[Invariant] Node Identity Key Generated: {self.public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex()[:16]}...")

    def execute(self, 
                input_payload: str,
                identity: Identity,
                model_spec: ModelSpec,
                context_spec: ContextSpec,
                policy_name: str = "default_policy") -> Dict[str, Any]:
        """
        The MANDATORY execution entry point.
        """
        print(f"\n--- Starting Invariant Execution ID: [Generated internally] ---")
        
        # 1. Load Policy (Compile & Load)
        # Resolve policy path if simple name
        if "/" not in policy_name and not policy_name.endswith(".json"):
             base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
             policy_path = os.path.join(base_dir, "policies", f"{policy_name}.json")
             if os.path.exists(policy_path):
                 policy_name = policy_path

        self.boundary.load_policy(policy_name)

        # 2. Freeze Configuration
        # Map Python ModelSpec to C++ ModelSpec
        cpp_model = enforcement.ModelSpec()
        cpp_model.provider = model_spec.provider
        cpp_model.name = model_spec.name
        cpp_model.version = model_spec.version
        cpp_model.seed = model_spec.seed
        cpp_model.decoding_strategy = model_spec.decoding_strategy
        
        self.boundary.load_model(cpp_model)

        # Map Python ContextSpec to C++ ContextSpec AND Update Python Objects with Hashes
        cpp_context = enforcement.ContextSpec()
        cpp_sources = []
        updated_py_sources = []

        for s in context_spec.sources:
            cpp_s = enforcement.ContextSource()
            cpp_s.type = s.type
            cpp_s.sensitivity = s.sensitivity
            cpp_s.identifier = s.identifier
            
            computed_hash = ""
            # Compute Hash if logical
            if s.type == "static" or s.type == "file":
                 path = s.identifier
                 if os.path.exists(path):
                     try:
                         # Use Native C++ Hashing for scalability
                         file_hash = enforcement.crypto_hash_file(path)
                         computed_hash = file_hash
                         print(f"[Invariant] Context Hash Computed (Native): {path} -> {file_hash[:12]}...")
                     except Exception as e:
                         print(f"[Invariant] Warning: Could not hash context file {path}: {e}")
                         computed_hash = "ERROR_HASH"
                 else:
                     # Fallback for "static" / memory mock sources
                     computed_hash = hashlib.sha256(s.identifier.encode()).hexdigest()
            
            cpp_s.content_hash = computed_hash
            cpp_sources.append(cpp_s)
            
            # Create updated Python source with the hash
            updated_py_sources.append(ContextSource(
                type=s.type,
                sensitivity=s.sensitivity,
                identifier=s.identifier,
                content_hash=computed_hash
            ))

        cpp_context.sources = cpp_sources
        self.boundary.load_context(cpp_context)
        
        # Create the definitive Execution Graph (Immutable Record)
        # We use the updated_py_sources so the record includes the actual hashes used
        final_context_spec = ContextSpec(updated_py_sources)
        execution_graph = ExecutionGraph(
            identity=identity,
            input_payload=input_payload,
            policy_name=policy_name,
            model=model_spec,
            context=final_context_spec
        )

        # 3. Admissibility Pre-Check (Delegated to C++)

        # 4. Resolve Model Adapter
        adapter = self._resolve_adapter(model_spec)
        
        # 5. Execution Loop (Streaming)
        # Usage of Token-Level Enforcement
        self.boundary.start(input_payload)
        
        # Stream tokens from adapter and feed to boundary
        generated_token_count = 0
        try:
             for token in adapter.generate(input_payload):
                 if not self.boundary.step(token):
                     print(f"[Invariant] Abort Triggered at token {generated_token_count}")
                     raise RuntimeError("Execution Aborted: Policy Violation Mid-Stream")
                 generated_token_count += 1
        except Exception as e:
             print(f"[Invariant] Stream Interrupted: {e}")
             # We might still want to seal what we have? 
             # For now, let it raise, but ideally we'd record the abort.
             raise e

        # Get the canonical output from the boundary
        output = self.boundary.get_output()

        # 6. Seal
        proof = self.boundary.seal()
        
        print(f"--- Execution Sealed. Proof: {proof} ---")
        
        return {
            "output": output,
            "proof": proof,
            "status": "COMPLETED",
            "graph": execution_graph
        }

    def save_record(self, result: Dict[str, Any], filepath: str):
        """
        Persist the full execution record (Graph + Proof + Output) to disk.
        Schema: invariant.receipt.v1
        """
        import json
        import datetime
        
        if "graph" not in result:
             raise ValueError("Result dictionary missing 'graph' object.")
        
        graph = result["graph"]
        
        # Schema V1.0 Definition
        receipt = {
            "schema": "invariant.receipt.v1",
            "meta": {
                "engine_version": "0.1.0",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "proof_id": result["proof"]
            },
            "graph": json.loads(graph.to_json()),
            "result": {
                "status": result["status"],
                "output": result["output"]
            },
            "integrity": {
                "signatures": [{
                    "algo": "ed25519",
                    "pub_key": self.public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw).hex(),
                    "signature": self.private_key.sign(result["proof"].encode("utf-8")).hex(),
                    "signed_field": "meta.proof_id"
                }] 
            }
        }
        
        with open(filepath, "w") as f:
            json.dump(receipt, f, indent=2)
        print(f"[Invariant] Execution Receipt V1 Saved: {filepath}")

    def _resolve_adapter(self, spec: ModelSpec) -> ModelAdapter:
        if spec.provider == "openai":
            try:
                from ai_execution_boundary.models.adapters.openai import OpenAIAdapter
            except ImportError as e:
                raise ImportError(f"Failed to load OpenAI adapter. Ensure 'openai' is installed and working: {e}")
            return OpenAIAdapter(spec)
        elif spec.provider == "mock":
            return MockAdapter(spec)
        else:
            raise ValueError(f"Unsupported provider: {spec.provider}")

# Singleton entry point for ease of use
_instance = Invariant()
def execute(*args, **kwargs):
    return _instance.execute(*args, **kwargs)
