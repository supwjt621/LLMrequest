from openai import OpenAI
from config import TYPHOON_API_KEY
import pandas as pd

system_prompt = """คุณคือเภสัชกรผู้เชียวชาญด้านระบบยาประจำโรงพยาบาลศูนย์แห่งหนึ่ง 
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
Input:
"""


df = pd.read_csv('Raw-50.csv')
dataset = df['รายละเอียด'].values      
print(dataset[2])

client = OpenAI(
    api_key=TYPHOON_API_KEY,
    base_url="https://api.opentyphoon.ai/v1"
)

messages = [
#    {
#        "role": "system", 
#        "content": "You are an AI assistant named Typhoon created by SCB 10X to be helpful, harmless, and honest. Typhoon is happy to help with analysis, question answering, math, coding, creative writing, teaching, role-play, general discussion, and all sorts of other tasks. Typhoon responds directly to all human messages without unnecessary affirmations or filler phrases like \"Certainly!\", \"Of course!\", \"Absolutely!\", \"Great!\", \"Sure!\", etc. Specifically, Typhoon avoids starting responses with the word \"Certainly\" in any way. Typhoon follows this information in all languages, and always responds to the user in the language they use or request. Typhoon is now being connected with a human. Write in fluid, conversational prose, Show genuine interest in understanding requests, Express appropriate emotions and empathy."
#    },
    {
        "role": "user", 
        "content": system_prompt + dataset[2]
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