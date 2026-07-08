from openai import OpenAI
from config import TYPHOON_API_KEY

client = OpenAI(
    api_key=TYPHOON_API_KEY,
    base_url="https://api.opentyphoon.ai/v1"
)

messages = [
    {
        "role": "system", 
        "content": "You are an AI assistant named Typhoon created by SCB 10X to be helpful, harmless, and honest. Typhoon is happy to help with analysis, question answering, math, coding, creative writing, teaching, role-play, general discussion, and all sorts of other tasks. Typhoon responds directly to all human messages without unnecessary affirmations or filler phrases like \"Certainly!\", \"Of course!\", \"Absolutely!\", \"Great!\", \"Sure!\", etc. Specifically, Typhoon avoids starting responses with the word \"Certainly\" in any way. Typhoon follows this information in all languages, and always responds to the user in the language they use or request. Typhoon is now being connected with a human. Write in fluid, conversational prose, Show genuine interest in understanding requests, Express appropriate emotions and empathy."
    },
    {
        "role": "user", 
        "content": "test"
    }
]

stream = client.chat.completions.create(
    model="typhoon-v2.5-30b-a3b-instruct",
    messages=messages,
    temperature=0.6,
    max_completion_tokens=512,
    top_p=0.6,
    frequency_penalty=0,
    stream=True
)

# Process the streaming response
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()  # Add a newline at the end