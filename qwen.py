import requests
import json
import pandas as pd
import time
from openai import OpenAI
from datetime import datetime
from config import QWEN_URL
from config import QWEN_MODEL
from config import QWEN_API_KEY
#from config import OLLAMA_MODEL  # you can define the model name in config.py

system_prompt = """คุณคือเภสัชกรผู้เชียวชาญด้านระบบยาประจำโรงพยาบาลศูนย์แห่งหนึ่ง 
ได้รับมอบหมายให้จัดประเภทของรายงานความคลาดเคลื่อนทางยาที่เกิดขึ้นในโรงพยาบาลตามมาตรฐานทางเภสัชกรรม ซึ่งมีทั้งหมด 5 ประเภท ได้แก่
* Prescribing Error เป็นความคลาดเคลื่อนในการสั่งใช้ยาของแพทย์, 
* Transcribing Error เป็นความคลาดเคลื่อนในการถ่ายทอดคำสั่งแพทย์มายังห้องยา, 
* Predispensing Error เป็นความคลาดเคลื่อนในการจัดยาในห้องยาก่อนส่งให้เภสัชกรตรวจสอบก่อนจ่ายยา, 
* Dispensing Error เป็นความคลาดเคลื่อนในการจ่ายยาของเภสัชกรออกจากห้องยา
* Administration Error เป็นความคลาดเคลื่อนในการบริหารยาโดยพยาบาล
ซึ่งรายงานความเสี่ยงแต่ละอุบัติการณ์ สามารถเกิดความคลาดเคลื่อนได้มากกว่า 1 ประเภท ทำให้การจัดประเภทในแต่ละอุบัติการณ์ สามารถตอบได้มากกว่า 1 ประเภท
##ตัวอย่างเหตุการณ์ความเสี่ยง 
1. Input: เภสัชกรจ่ายยาผิดชื่อยาไปยังหอผู้ป่วย และพยาบาลบนหอผู้ป่วยได้ให้ยาไป 1 มื้อ
* Rationale: เนื่องจาก เภสัชกรเป็นผู้จ่ายยา แต่ยาที่จ่ายออกมามีชื่อไม่ตรงกับคำสั่งใช้ยาของแพทย์ ซึ่งเมื่อยาจ่ายออกไปที่หอผู้ป่วย พยาบาลก็ไม่ได้ตรวจสอบชื่อยาว่าตรงกับคำสั่งแพทย์หรือไม่ จึงให้ยาที่ผิดชื่อแก่ผู้ป่วย
* Output: Dispensing Error, Administration Error
2. Input: ไม่ได้สั่งยาเดิม metformin ให้ผู้ป่วยกลับบ้าน 
* Rationale: เดิมผู้ป่วยมียารักษาโรคประจำตัว แต่แพทย์ไม่ได้สั่งใช้ยาเหล่านี้ต่อในวันกลับบ้าน จึงถือเป็นความผิดพลาดจากการสั่งใช้ยาของแพทย์
* Output: Prescribing Error
##Output Rules: ให้ตอบเป็นข้อความธรรมดา โดยตอบเฉพาะชื่อหมวดหมู่ที่กำหนดเท่านั้น ทั้งนี้ อาจตอบได้มากกว่า 1 หมวดหมู่ก็ได้ หากมีมากกว่า 1 หมวดหมู่ ให้คั่นแต่ละหมวดหมู่ด้วยเครื่องหมาย ","
คำตอบที่อนุญาต: 'Prescribing Error', 'Transcribing Error', 'Predispensing Error', 'Dispensing Error', 'Administration Error'
ห้าม: ใส่หมายเลข, ใส่เครื่องหมายคำพูด, อธิบายเพิ่มเติม
##จงจัดประเภทรายงานความเสี่ยงต่อไปนี้ โดยตอบเฉพาะประเภทความคลาดเคลื่อนที่กำหนดเท่านั้น
Input:
"""

# Ollama typically runs on http://localhost:11434
#OLLAMA_URL = "http://192.168.1.120:11434/api/generate"
#model_name = "qwen3:0.6b"

OLLAMA_URL = QWEN_URL
model_name = QWEN_MODEL
API_KEY = QWEN_API_KEY
counter = 3

def readFile() -> str:
    df = pd.read_csv('./Assets/Raw-50.csv')
    dataset = df['รายละเอียด'].values 
    repcode = df['รหัสรายงาน'].values
    ansSet = []   

    for i in range(counter):
        print("\n" + dataset[i])
        result = AskOllama(system_prompt + dataset[i] + "\nOutput:")
        ansSet.append(result)

    nows = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
    df_set = pd.DataFrame({
        'รหัสรายงาน' : repcode[:counter],
        'รายละเอียด' : dataset[:counter],
        'คำตอบ' : ansSet
    })
    df_set.to_csv("./Result_log/" + model_name.replace(":", "-") + '_' + nows + '.csv', index=False, encoding='utf-8-sig')
    print('Exported to '+ model_name.replace(":", "-") + '_' + nows + '.csv')


def generate_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text."""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": True,          # we want a streaming response like OpenAI
        "max_tokens": 4096,       # optional – adjust as needed
        "think": False
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
    client = OpenAI(api_key=API_KEY, base_url=OLLAMA_URL)
    full_response = ""
    is_reasoning = False

    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        extra_body={"enable_thinking": False},
        stream=True
    )

    for chunk in stream:
        if not chunk.choices:
            continue
        
        delta = chunk.choices[0].delta

        # Stream reasoning content as it arrives
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            if not is_reasoning:
                print("[Reasoning]\n", end="", flush=True)
                is_reasoning = True
            
            print(delta.reasoning_content, end="", flush=True)

        # Stream and accumulate standard response message
        elif delta.content:
            if is_reasoning:
                print("\n\n[Response]\n", end="", flush=True)
                is_reasoning = False
            
            full_response += delta.content
            print(delta.content, end="", flush=True)

    print()  # Final newline when completed
    return full_response




# ----------------------------------------------------------------------
# Example usage – same prompt as before
# ----------------------------------------------------------------------
if __name__ == "__main__":
    #stream_text = generate_ollama( input("\nAsk anything:") )
    readFile()
    # If you need a final newline or any post‑processing, do it here.