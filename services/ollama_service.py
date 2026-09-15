import json
import requests
from config import settings

def generate_stream(prompt: str):
    """Stream response from Ollama model"""
    response = requests.post(
        f"{settings.OLLAMA_URL}/api/generate",
        json={
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            yield data.get("response", "")
