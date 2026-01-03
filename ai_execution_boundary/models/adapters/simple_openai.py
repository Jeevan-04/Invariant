import os
import json
import requests
from typing import Iterator
from .base import ModelAdapter
from ...control.execution_graph import ModelSpec

class SimpleOpenAIAdapter(ModelAdapter):
    """
    A lightweight adapter that uses `requests` directly.
    Avoids the heavy `openai` python package and its pydantic dependency issues.
    """
    def __init__(self, model_spec: ModelSpec):
        self.model_spec = model_spec
        # Expect key in env, as set by app.py
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def generate(self, prompt: str) -> Iterator[str]:
        if not self.api_key:
             yield " [System: Please enter an API Key in the sidebar.]"
             return

        # Default Endpoint: OpenAI
        url = "https://api.openai.com/v1/chat/completions"
        model_name = "gpt-3.5-turbo"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # OpenRouter Configuration (Preferred)
        if self.api_key.startswith("sk-or-"):
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers["HTTP-Referer"] = "https://invariant.app"
            headers["X-Title"] = "Invariant Kernel"
            # Default to a solid model on OpenRouter, or keep requesting gpt-3.5 and let them map it
            # But let's try to ask for 'google/gemini-2.0-flash-exp:free' or just 'gpt-3.5-turbo'?
            # Sticking to standard for compatibility unless user changed it.
            model_name = "gpt-3.5-turbo" 

        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "stream": True # Force streaming for kernel interception
        }
        
        try:
            with requests.post(url, headers=headers, json=data, stream=True) as r:
                if r.status_code != 200:
                    yield f" [API Error {r.status_code} from {url}: {r.text}]"
                    return
                
                # Standard SSE Parser (Works for OpenAI & OpenRouter)
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data: "):
                            content = decoded[6:]
                            if content == "[DONE]": 
                                break
                            try:
                                chunk = json.loads(content)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0]["delta"].get("content", "")
                                    if delta: 
                                        yield delta
                            except Exception:
                                pass
        except Exception as e:
            yield f" [Network Exception: {e}]"
