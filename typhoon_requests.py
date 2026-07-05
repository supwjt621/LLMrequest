import requests
import json

# API configuration
token = "sk-xtB9FyvehRtukgCOl6ST8mgPWrw74mADrnhBrLvFuVaoF3dR"
base_url = "https://api.opentyphoon.ai/v1"
model = "typhoon-v2.5-30b-a3b-instruct"

# Request headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Messages payload
messages = [
    {
        "role": "system", 
        "content": "You are an AI assistant named Typhoon created by SCB 10X to be helpful, harmless, and honest. Typhoon is happy to help with analysis, question answering, math, coding, creative writing, teaching, role-play, general discussion, and all sorts of other tasks. Typhoon responds directly to all human messages without unnecessary affirmations or filler phrases like \"Certainly!\", \"Of course!\", \"Absolutely!\", \"Great!\", \"Sure!\", etc. Specifically, Typhoon avoids starting responses with the word \"Certainly\" in any way. Typhoon follows this information in all languages, and always responds to the user in the language they use or request. Typhoon is now being connected with a human. Write in fluid, conversational prose, Show genuine interest in understanding requests, Express appropriate emotions and empathy."
    },
    {
        "role": "user", 
        "content": "สวัสดี"
    }
]

# Request payload
payload = {
    "model": model,
    "messages": messages,
    "temperature": 0.6,
    "max_tokens": 512,
    "top_p": 0.6,
    "frequency_penalty": 0
}

# Make the streaming request
response = requests.post(
    f"{base_url}/chat/completions",
    headers=headers,
    json=payload,
    stream=True
)


# Process the streaming response
if response.status_code == 200:
    # Initialize variables to accumulate the response
    full_response = ""
    
    # Stream the response and yield tokens as they arrive
    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            decoded_chunk = chunk.decode('utf-8')
            # Remove 'data: ' prefix and ' [DONE]' suffix from each chunk
            lines = decoded_chunk.strip().split('\n')
            for line in lines:
                # Print raw line for debugging
                # print(f"Raw line: {line}")
                resp = json.loads(line)
                print(resp["choices"][0]["message"]["content"])