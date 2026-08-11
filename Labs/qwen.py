from openai import OpenAI
import os
from config import QWEN_API_KEY

sys_prompt = ""

script_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(script_dir, "..", "Prompts", "sys_prompt_v2.md")

with open(md_path, "r", encoding="utf-8") as file:
    sys_prompt = file.read()

client = OpenAI(
    # If the environment variable is not set, replace it with your Model Studio API key: api_key="sk-xxx"
    api_key=QWEN_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

messages = [
    { "role": "system", "content": sys_prompt },
    { "role": "user", "content": "ช่วยจำแนกประเภทความเสี่ยงต่อไปนี้ให้หน่อย: "+ input("\nIncidence: ") }
]
completion = client.chat.completions.create(
    model="qwen3.5-flash",  # You can replace this with another deep thinking models
    messages=messages,
    extra_body={"enable_thinking": True},
    stream=True
)

is_answering = False  # Indicates whether the response phase has started
print("\n" + "=" * 20 + "Thinking process" + "=" * 20)
for chunk in completion:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "Full response" + "=" * 20)
            is_answering = True
        print(delta.content, end="", flush=True)