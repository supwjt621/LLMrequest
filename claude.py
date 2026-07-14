import os
from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-3-5-sonnet-latest",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a short poem about coding."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)