import requests
import json
from config import THAI_LLM_KEY

APIkey = THAI_LLM_KEY
URLs = "http://thaillm.or.th/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + APIkey,
}

def ContinuePrompt():
    while True:
        Question = input("\nAsk anything>> ")
        if Question == "Quit":
            print("Exiting application...")
            break

        data = {
            "model": "openthaigpt-thaillm-8b-instruct-v7.2",
            "messages": [ {"role": "user", "content": Question} ],
            "max_tokens": 2048,
            "temperature": 0.3,
        }
        
        try:
            response = requests.post(URLs, json=data, headers=headers, stream=True)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection failed: {e}") 
            break

        if response.status_code == 200:
            for line in response.iter_lines():
                if not line:
                    continue

                line = line.decode("utf-8")

                # OpenAI-compatible APIs send "data: ..."
                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break

                    chunk = json.loads(data)

                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        print(delta["content"], end="", flush=True)

                    print()
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    ContinuePrompt()