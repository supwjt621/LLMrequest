import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
import pandas as pd

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
Input: เภสัชกรจ่ายยาผิดชื่อยาไปยังหอผู้ป่วย
Rationale: เนื่องจาก เภสัชกรเป็นผู้จ่ายยา แต่ยาที่จ่ายออกมามีชื่อไม่ตรงกับคำสั่งใช้ยาของแพทย์ ซึ่งเมื่อยาจ่ายออกไปที่หอผู้ป่วย พยาบาลเป็นผู้ตรวจสอบพบคลาดเคลื่อนนี้
Output: Dispensing Error
Input: ไม่ได้สั่งยาเดิม metformin ให้ผู้ป่วยกลับบ้าน
Rationale: เดิมผู้ป่วยมียารักษาโรคประจำตัว แต่แพทย์ไม่ได้สั่งใช้ยาเหล่านี้ต่อในวันกลับบ้าน จึงถือเป็นความผิดพลาดจากการสั่งใช้ยาของแพทย์
Output: Prescribing Error
##Output Rules: ให้ตอบเป็นข้อความธรรมดา โดยตอบเฉพาะชื่อหมวดหมู่ที่กำหนด พร้อมเหตุผลสั้น ๆ 1 บรรทัด ทั้งนี้ อาจตอบได้มากกว่า 1 หมวดหมู่ก็ได้
คำตอบที่อนุญาต: 'Prescribing Error', 'Transcribing Error', 'Predispensing Error', 'Dispensing Error', 'Administration Error'
ห้าม: ใส่หมายเลข, ใส่เครื่องหมายคำพูด
##จงจัดประเภทรายงานความเสี่ยงต่อไปนี้ โดยตอบเฉพาะประเภทความคลาดเคลื่อนที่กำหนดเท่านั้น
"""


df = pd.read_csv('Raw-50.csv')
dataset = df['รายละเอียด'].values      


if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file or system.")

# Set the API key
os.environ["GEMINI_API_KEY"] = api_key

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

client = genai.Client()

with open("alteplase.md", "r") as f:
    file_content = f.read()

# 1. Define the Specialist Persona and Rules
system_prompt = systemPrompt

# 2. Send the Request
# We include the system_instruction in the config
interaction = client.models.generate_content_stream(
    model="gemini-3.5-flash",
    contents=[
        {"role": "user", "parts": [{"text": "Input:" + dataset[3] + "\nOutput:"}]},
        #{"role": "user", "parts": [{"text": f"Reference Data:\n{file_content}"}]}
    ],
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json" # Ensures strict JSON output
    )
)

print(dataset[3])

# 3. Process the Response
for i, chunk in enumerate(interaction, 1):
    print(chunk.text, end="", flush=True)   # live output
    # optionally process chunk here...
print()  # newline after the loop ends

