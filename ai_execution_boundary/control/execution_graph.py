from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum
import hashlib
import json

class DeterminismLevel(Enum):
    STRICT = "STRICT"
    BOUNDED = "BOUNDED"
    BEST_EFFORT = "BEST_EFFORT"

@dataclass(frozen=True)
class Identity:
    """
    Represents the identity triggering the execution.
    Mandatory: user_id, role, org, env.
    No anonymous executions allowed.
    """
    user_id: str
    role: str
    org: str
    env: str

    def __post_init__(self):
        if not all([self.user_id, self.role, self.org, self.env]):
            raise ValueError("Identity fields cannot be empty")

@dataclass(frozen=True)
class ModelSpec:
    """
    Defines the exact model configuration.
    Must include version, seed, and decoding strategy to ensure replayability.
    """
    provider: str
    name: str
    version: str
    seed: int
    decoding_strategy: str  # e.g., "greedy", "temperature=0.7"
    
    # Optional parameters for specific decoding strategies, but kept minimal for now
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not all([self.provider, self.name, self.version, self.decoding_strategy]):
            raise ValueError("ModelSpec must strictly define provider, name, version, and decoding")
        if self.seed is None:
             raise ValueError("Seed must be explicitly set")

@dataclass(frozen=True)
class ContextSource:
    type: str # e.g., "rag", "memory", "tool", "static"
    sensitivity: str # e.g., "public", "internal", "restricted"
    identifier: str # URI/Filename
    content_hash: str = "" # SHA256 of the content

@dataclass(frozen=True)
class ContextSpec:
    """
    Explicit declaration of all context sources used in this execution.
    Context is declared, not discovered.
    """
    sources: List[ContextSource]

@dataclass(frozen=True)
class ExecutionGraph:
    """
    The immutable graph representing the planned execution.
    This object is what gets sealed and proved.
    """
    identity: Identity
    input_payload: str # The raw prompt/input
    policy_name: str
    model: ModelSpec
    context: ContextSpec
    
    # Calculated fields
    id: str = field(init=False)
    
    def __post_init__(self):
        # Generate a deterministic ID based on the graph contents (simplified for V0)
        # In a real impl, this would be a deep recursive hash of all fields
        object.__setattr__(self, 'id', self._generate_hash())

    def _generate_hash(self) -> str:
        data = {
            "identity": str(self.identity),
            "input": self.input_payload,
            "policy": self.policy_name,
            "model": str(self.model),
            "context": str(self.context)
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def to_json(self) -> str:
         # Simple serialization for debug/transport
         # Production needs strictly deterministic serialization (Protobuf/Flatbuffers)
         return json.dumps({
            "id": self.id,
            "identity": self.identity.__dict__,
            "input_payload": self.input_payload,
            "policy_name": self.policy_name,
            "model": {
                **self.model.__dict__, 
                "extra_params": self.model.extra_params
            },
            "context": {
                "sources": [s.__dict__ for s in self.context.sources]
            }
         }, indent=2)
