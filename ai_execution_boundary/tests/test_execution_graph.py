from ai_execution_boundary.control.execution_graph import Identity, ModelSpec, ContextSpec, ExecutionGraph, ContextSource
import json

def test_identity_validation():
    # Valid identity
    id = Identity("user1", "admin", "acme", "prod")
    assert id.user_id == "user1"

    # Invalid identity (empty fields)
    try:
        Identity("", "admin", "acme", "prod")
        raise AssertionError("Should have raised ValueError for empty Identity fields")
    except ValueError:
        pass

def test_model_spec_validation():
    # Valid spec
    spec = ModelSpec("openai", "gpt-4", "v1", 42, "greedy")
    assert spec.seed == 42

    # Invalid spec (missing seed)
    try:
        ModelSpec("openai", "gpt-4", "v1", None, "greedy")
        raise AssertionError("Should have raised ValueError for missing seed")
    except ValueError:
        pass

def test_execution_graph_hashing():
    id = Identity("user1", "admin", "acme", "prod")
    model = ModelSpec("openai", "gpt-4", "v1", 42, "greedy")
    context = ContextSpec([ContextSource("rag", "internal", "hash1")])
    
    graph1 = ExecutionGraph(id, "test_input", "policy_v1", model, context)
    graph2 = ExecutionGraph(id, "test_input", "policy_v1", model, context)
    
    # Hash should be deterministic and identical for identical inputs
    assert graph1.id == graph2.id
    
    # Change one field
    graph3 = ExecutionGraph(id, "test_input_DIFFERENT", "policy_v1", model, context)
    assert graph1.id != graph3.id

if __name__ == "__main__":
    try:
        test_identity_validation()
        print("test_identity_validation PASSED")
        test_model_spec_validation()
        print("test_model_spec_validation PASSED")
        test_execution_graph_hashing()
        print("test_execution_graph_hashing PASSED")
        print("All tests passed!")
    except Exception as e:
        print(f"Tests FAILED: {e}")
        exit(1)
