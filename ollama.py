import requests
import json
#from config import OLLAMA_MODEL  # you can define the model name in config.py

# Ollama typically runs on http://localhost:11434
OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text."""
    payload = {
        "model": "qwen3:0.6b",
        "prompt": prompt,
        "stream": True,          # we want a streaming response like OpenAI
        "max_tokens": 1024,       # optional – adjust as needed
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    response.raise_for_status()  # will raise if something went wrong

    # Ollama’s streaming response is a series of JSON lines; collect them
    generated = ""
    for line in response.iter_lines():
        if line:
            # The actual JSON payload is after the "data:" prefix
            json_part = line
            if json_part:
                chunk = json.loads(json_part)
                # The text chunk is usually under `response` -> "message" -> "content"
                chunk_text = chunk.get("response", "")
                print(chunk_text, end="", flush=True)
                generated += chunk_text
    return generated


# ----------------------------------------------------------------------
# Example usage – same prompt as before
# ----------------------------------------------------------------------
if __name__ == "__main__":
    stream_text = generate_ollama(
        input("\nAsk anything:")
    )
    # If you need a final newline or any post‑processing, do it here.