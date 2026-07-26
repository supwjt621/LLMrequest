import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

api_key = GEMINI_API_KEY

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file or system.")

# Set the API key
os.environ["GEMINI_API_KEY"] = api_key


os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

client = genai.Client()

with open("alteplase.md", "r") as f:
    file_content = f.read()

# 1. Define the Specialist Persona and Rules
system_prompt = """
You are an experienced medical practitioner and clinical pharmacology assistant.
"""

# 2. Send the Request
# We include the system_instruction in the config
interaction = client.models.generate_content_stream(
    model="gemini-3.5-flash",
    contents=[
        {"role": "user", "parts": [{"text": "Question: " + input("\nAsk anything>> ")}]},
        #{"role": "user", "parts": [{"text": f"Reference Data:\n{file_content}"}]}
    ],
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json" # Ensures strict JSON output
    )
)

# 3. Process the Response
for i, chunk in enumerate(interaction, 1):
    print(chunk.text, end="", flush=True)   # live output
    # optionally process chunk here...
print()  # newline after the loop ends

