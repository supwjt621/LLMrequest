import requests
import json
import os
import pandas as pd
import time
from datetime import datetime

#from config import OLLAMA_MODEL  # you can define the model name in config.py
script_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(script_dir, "..", "Prompts", "sys_prompt_v3.md")

system_prompt = ""

with open(md_path, "r", encoding="utf-8") as file:
    system_prompt = file.read()

# Ollama typically runs on http://localhost:11434
#OLLAMA_URL = "http://192.168.1.120:11434/api/generate"
model_name = "qwen3:0.6b"

OLLAMA_URL = "http://localhost:11434/api/generate"

counter = 5

def readFile() -> str:
    df = pd.read_csv('Assets/Raw-50.csv')
    dataset = df['รายละเอียด'].values 
    repcode = df['รหัสรายงาน'].values
    ansSet = []   

    for i in range(counter):
        print("\n" + dataset[i])
        result = AskOllama(system_prompt + "จงจำแนกประเภทของอุบัติการณ์ความเสี่ยงดังต่อไปนี้" + dataset[i])
        ansSet.append(result)
        print(result)

    nows = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
    df_set = pd.DataFrame({
        'รหัสรายงาน' : repcode[:counter],
        'รายละเอียด' : dataset[:counter],
        'คำตอบ' : ansSet
    })
    df_set.to_csv(f"Result_log/{model_name.replace(":", "-")}_{nows}.csv", index=False, encoding='utf-8-sig')
    print('\nExported to '+ model_name.replace(":", "-") + '_' + nows + '.csv')


def generate_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text."""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": True,          # we want a streaming response like OpenAI
        "max_tokens": 8192,       # optional – adjust as needed
        "think": True
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


def AskOllama(prompt: str) -> str:
    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 2048,
        "think": False,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=False)
    resp = response.json()
    return resp['response']

# ----------------------------------------------------------------------
# Example usage – same prompt as before
# ----------------------------------------------------------------------
if __name__ == "__main__":
    #stream_text = generate_ollama( input("\nAsk anything:") )
    readFile()
    # If you need a final newline or any post‑processing, do it here.