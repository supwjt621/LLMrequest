import requests
import json
from config import THAI_LLM_KEY

APIkey = THAI_LLM_KEY
URLs = "http://thaillm.or.th/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + APIkey,
}

sys_prompt = ""

with open("Assets/sys_prompt_v2.md", "r", encoding="utf-8") as file:
    sys_prompt = file.read()


def ContinuePrompt():
    while True:
        Question = input("\nAsk anything>> ")
        if Question.lower() == "quit":
            print("Exiting application...")
            break

        data = {
            "model": "thalle-0.2-thaillm-8b-fa",
            "messages": [ 
                { "role": "user", "content": "ช่วยจำแนกอุบัติการณ์ความเสี่ยงต่อไปนี้: " + Question }, 
                { "role": "system", "content": sys_prompt }
            ],
            "max_tokens": 8192,
            "temperature": 0.3,
            "stream": True,
            "think": False
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
            print("\n")
                    
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    ContinuePrompt()