from openai import OpenAI
from config import TYPHOON_API_KEY
from config import LOCAL_OLLAMA_URL
from config import LOCAL_OLLAMA_APIKEY
import pandas as pd
import time
from datetime import datetime

client = OpenAI(
    api_key=LOCAL_OLLAMA_APIKEY,
    base_url=LOCAL_OLLAMA_URL
)

sys_prompt = """คุณคือเภสัชกรผู้เชียวชาญด้านระบบยาประจำโรงพยาบาลศูนย์แห่งหนึ่ง 
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
reportcode = df['รหัสรายงาน'].values
counter = 3

def ContChat():
    answers = []
    for i in range(counter):   
        userMsg = dataset[i]
        print("\n" + userMsg)
        if userMsg.lower() == 'quit':
            print('Exiting Application...')
            break

        messages = [
            { "role": "system", "content": sys_prompt },
            { "role": "user", "content": userMsg }
        ]

        stream = client.chat.completions.create(
            model="qwen3.6:27b",
            messages=messages,
            temperature=0.6,
            max_completion_tokens=4096,
            top_p=0.6,
            frequency_penalty=0,
            stream=True
        )

        # Process the streaming response
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                print(chunk.choices[0].delta.content, end="", flush=True)

        print()  # Add a newline at the end
        answers.append(full_response.replace("\n", ","))
        time.sleep(3)
    return answers

if __name__ == "__main__":
    ansSet = ContChat()

    df_result = pd.DataFrame({
        'รหัสรายงาน' : reportcode[:counter],
        'รายละเอียด': dataset[:counter],
        'คำตอบ' : ansSet
    })
    nows = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
    df_result.to_csv('typhoon_' + nows + '.csv', index=False, encoding='utf-8-sig')