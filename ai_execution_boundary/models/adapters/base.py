from abc import ABC, abstractmethod
from typing import Iterator
from ai_execution_boundary.control.execution_graph import ModelSpec

class ModelAdapter(ABC):
    """
    Abstract base class for all Model Adapters.
    Adapters are responsible for:
    1. Communicating with the specific provider (API or local).
    2. Respecting the ModelSpec (seed, config).
    3. Normalizing output into a string iterator.
    """
    
    def __init__(self, model_spec: ModelSpec):
        self.spec = model_spec

    @abstractmethod
    def generate(self, prompt: str) -> Iterator[str]:
        """
        Generates text from the model.
        Must return a token iterator to allow the boundary to intercept per-token.
        """
        pass
