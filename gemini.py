import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import pandas as pd
import time
from datetime import datetime

api_key = GEMINI_API_KEY

systemPrompt = """คุณคือเภสัชกรผู้เชียวชาญด้านระบบยาประจำโรงพยาบาลศูนย์แห่งหนึ่ง 
ได้รับมอบหมายให้จัดประเภทของรายงานความคลาดเคลื่อนทางยาที่เกิดขึ้นในโรงพยาบาลตามมาตรฐานทางเภสัชกรรม ซึ่งมีทั้งหมด 5 ประเภท ได้แก่
* Prescribing Error เป็นความคลาดเคลื่อนในการสั่งใช้ยาของแพทย์, 
* Transcribing Error เป็นความคลาดเคลื่อนในการถ่ายทอดคำสั่งแพทย์มายังห้องยา, 
* Predispensing Error เป็นความคลาดเคลื่อนในการจัดยาในห้องยาก่อนส่งให้เภสัชกรตรวจสอบก่อนจ่ายยา, 
* Dispensing Error เป็นความคลาดเคลื่อนในการจ่ายยาของเภสัชกรออกจากห้องยา
* Administration Error เป็นความคลาดเคลื่อนในการบริหารยาโดยพยาบาล
ซึ่งรายงานความเสี่ยงแต่ละอุบัติการณ์ สามารถเกิดความคลาดเคลื่อนได้มากกว่า 1 ประเภท ทำให้การจัดประเภทในแต่ละอุบัติการณ์ สามารถตอบได้มากกว่า 1 ประเภท
##ตัวอย่างเหตุการณ์ความเสี่ยง 
1. Input: เภสัชกรจ่ายยาผิดชื่อยาไปยังหอผู้ป่วย
* Rationale: เนื่องจาก เภสัชกรเป็นผู้จ่ายยา แต่ยาที่จ่ายออกมามีชื่อไม่ตรงกับคำสั่งใช้ยาของแพทย์ ซึ่งเมื่อยาจ่ายออกไปที่หอผู้ป่วย พยาบาลเป็นผู้ตรวจสอบพบคลาดเคลื่อนนี้
* Output: Dispensing Error
2. Input: ไม่ได้สั่งยาเดิม metformin ให้ผู้ป่วยกลับบ้าน
* Rationale: เดิมผู้ป่วยมียารักษาโรคประจำตัว แต่แพทย์ไม่ได้สั่งใช้ยาเหล่านี้ต่อในวันกลับบ้าน จึงถือเป็นความผิดพลาดจากการสั่งใช้ยาของแพทย์
* Output: Prescribing Error
##Output Rules: ให้ตอบเป็นข้อความธรรมดา โดยตอบเฉพาะชื่อหมวดหมู่ที่กำหนดเท่านั้น ทั้งนี้ อาจตอบได้มากกว่า 1 หมวดหมู่ก็ได้แต่ให้คั่นด้วยเครื่องหมาย comma เท่านั้น
คำตอบที่อนุญาต: 'Prescribing Error', 'Transcribing Error', 'Predispensing Error', 'Dispensing Error', 'Administration Error'
ห้าม: ใส่หมายเลข, ใส่เครื่องหมายคำพูด, อธิบายเพิ่มเติม
##จงจัดประเภทรายงานความเสี่ยงต่อไปนี้ โดยตอบเฉพาะประเภทความคลาดเคลื่อนที่กำหนดเท่านั้น
Input:
"""

df = pd.read_csv('./Assets/Raw-50.csv')
dataset = df['รายละเอียด'].values     
codeSet = df['รหัสรายงาน'].values


if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file or system.")

# Set the API key
os.environ["GEMINI_API_KEY"] = api_key
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

client = genai.Client()

# 1. Define the Specialist Persona and Rules
system_prompt = systemPrompt
counter = 10
model_name = "gemini-3.5-flash-lite"

def makeRequest():
    ansSet = []
    
    for i in range(10):
        interaction = client.models.generate_content_stream(
            model=model_name,
            contents=[
                {"role": "user", "parts": [{"text": "Input:" + dataset[i] + "\nOutput:"}]},
                #{"role": "user", "parts": [{"text": f"Reference Data:\n{file_content}"}]}
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json" # Ensures strict JSON output
            )
        )
        print("\n" + dataset[i])
        fullResp = ""
        # 3. Process the Response
        for i, chunk in enumerate(interaction, 1):
            fullResp += chunk.text
            print(chunk.text, end="", flush=True)   # live output
            # optionally process chunk here...
        ansSet.append(fullResp)

    data_export = pd.DataFrame({
        'รหัสรายงาน': codeSet[:counter],
        'รายละเอียด': dataset[:counter],
        'คำตอบ': ansSet
    })
    nows = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
    data_export.to_csv(f"Assets/{model_name} + '_' + {nows} + '.csv", index=False, encoding='utf-8-sig')
    print(f"\nExported to ./Assets/{model_name} + '_' + {nows} + '.csv")

if __name__ == "__main__":
    makeRequest()