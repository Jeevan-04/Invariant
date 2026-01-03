import os
from typing import Iterator
from openai import OpenAI
from .base import ModelAdapter

class OpenAIAdapter(ModelAdapter):
    """
    Adapter for OpenAI's Chat Completion API.
    Strictly enforces the configuration provided in ModelSpec.
    """
    
    def __init__(self, model_spec):
        super().__init__(model_spec)
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL")
        
        # Check for overrides in spec
        if "api_key" in self.spec.extra_params:
            api_key = self.spec.extra_params["api_key"]
        if "base_url" in self.spec.extra_params:
            base_url = self.spec.extra_params["base_url"]

        if not api_key:
            # We don't raise here, we raise at generation time or let OpenAI lib handle it,
            pass
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str) -> Iterator[str]:
        # Parse decoding strategy (simplified for V0)
        # Expect strategy string like "greedy" or "temperature=0.7"
        temperature = 0.0
        if "temperature=" in self.spec.decoding_strategy:
            try:
                temperature = float(self.spec.decoding_strategy.split("=")[1])
            except:
                pass # Default to 0.0
        
        # Call OpenAI with strict parameters
        response = self.client.chat.completions.create(
            model=self.spec.name, # e.g., "gpt-4"
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            seed=self.spec.seed, # CRITICAL: Enforce server-side determinism
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
