import requests
from config import OPENROUTER_API_KEY

# Set your API key here
api_key = OPENROUTER_API_KEY

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Get user input for model and message
model = input("Enter model (e.g., openrouter/free): ").strip() or "openrouter/free"
message = input("Enter your message: ").strip() or "test"

data = {
    "model": model,
    "messages": [{"role": "user", "content": message}]
}

response = requests.post(url, json=data, headers=headers)
resp = response.json()
# Print the response
print(resp['model'])
print(resp['choices'][0]['message']['content'])