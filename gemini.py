from google import genai
from google.genai import types

client = genai.Client()

# 1. Define the Specialist Persona and Rules
system_prompt = """
You are a Senior Financial Risk Analyst. 
Your task is to classify customer transaction descriptions into one of three categories: 
'Fraudulent', 'Legitimate', or 'Review Required'.

Rules:
- Output only JSON format.
- Schema: {"category": "string", "reasoning": "string"}
- If the description is ambiguous, classify as 'Review Required'.
"""

# 2. Send the Request
# We include the system_instruction in the config
interaction = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Transaction: 'Unexpected high-value payment to offshore account at 3 AM'",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json" # Ensures strict JSON output
    )
)

print(interaction.text)