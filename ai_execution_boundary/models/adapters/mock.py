from typing import Iterator
import time
from .base import ModelAdapter

class MockAdapter(ModelAdapter):
    """
    A deterministic mock adapter that generates predictable text.
    Used for testing the core loop without making network calls.
    """
    
    def generate(self, prompt: str) -> Iterator[str]:
        # Simple deterministic generation based on seed
        seed_offset = self.spec.seed % 5
        responses = [
            "This is a deterministic response A.",
            "This is a deterministic response B.",
            "Execution is proceeding normally.",
            "Invariant system test response.",
            "Checking policy compliance now."
        ]
        
        response = responses[seed_offset]
        
        # Simulate token streaming
        for word in response.split():
            yield word + " "
            # No sleep here to keep tests fast, but could be added for realism
