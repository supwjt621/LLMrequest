import requests
import json
import os
import pandas as pd

#from config import OLLAMA_MODEL  # you can define the model name in config.py
script_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(script_dir, "..", "Prompts", "sys_prompt_v4.md")
usr_path = os.path.join(script_dir, "..", "Prompts", "user_prompt.md")
kb_path = os.path.join(script_dir, "..", "Prompts", "CPM_classifier.json")

OLLAMA_URL = "http://localhost:11434/api/chat"
model_name = "qwen3.5:0.8b"

system_prompt1 = system_prompt2 = ""
user_prompt1 = user_prompt2 = ""
cpm_knowledge_base = ""

counter = 1

def readPrompt():
    global system_prompt1, system_prompt2, user_prompt1, user_prompt2, cpm_knowledge_base

    #read system prompt
    with open(md_path, "r", encoding="utf-8") as file:
        system_prompt = file.readlines()

    ExtractPart = 0
    for line in system_prompt:
        if line.startswith("# End") and ExtractPart != 0:
            ExtractPart = 0
        elif line.startswith("# Prompt_1") or ExtractPart == 1:
            ExtractPart = 1
            system_prompt1 += line.strip()
        elif line.startswith("# Prompt_2") or ExtractPart == 2:
            ExtractPart = 2
            system_prompt2 += line.strip()

    print("system_prompt added")
    system_prompt1 = system_prompt1.replace("# Prompt_1", "")
    system_prompt2 = system_prompt2.replace("# Prompt_2", "")

    #read user_prompt
    with open(usr_path, "r", encoding="utf-8") as file:
        user_prompt = file.readlines()

    ExtractPart = 0
    for line in user_prompt:
        if line.startswith("# End") and ExtractPart != 0:
            ExtractPart = 0
        elif line.startswith("# Prompt_1") or ExtractPart == 1:
            ExtractPart = 1
            user_prompt1 += line.strip()
        elif line.startswith("# Prompt_2") or ExtractPart == 2:
            ExtractPart = 2
            user_prompt2 += line.strip()

    user_prompt1 = user_prompt1.replace("# Prompt_1", "")
    user_prompt2 = user_prompt2.replace("# Prompt_2", "")
    print("user_prompt added")

    #read Knowledge base
    with open(kb_path, "r", encoding="utf-8") as file:
        cpm_knowledge_base = file.read()

    print("knowledge base added")
    return
#End def

def readFile() -> str:
    df = pd.read_csv('Assets/Raw-50.csv')
    dataset = df['รายละเอียด'].values 
    repcode = df['รหัสรายงาน'].values
    ansSet = []   

    for i in range(counter):
        print("\n" + dataset[i])
        result = generate_ollama(system_prompt1, user_prompt1 + dataset[i] + "\nOutput:")
        
        prompt2 = user_prompt2 + "Input Data: Incident text: " + dataset[i] + ", Core Facts from Step 1: " + result + "\nOutput: "
        result2 = generate_ollama(system_prompt2, prompt2)

        result = result.strip().replace("```json", "").replace("```", "")
        result2 = result2.strip().replace("```json", "").replace("```", "")

        extracted_facts = prepare_facts(json.loads(result), json.loads(result2))
        matched_results = match_cpm(cpm_knowledge_base, extracted_facts)
        ansSet.append(matched_results)

    for j in len(ansSet):
        print(ansSet[j])

    '''
    nows = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
    df_set = pd.DataFrame({
        'รหัสรายงาน' : repcode[:counter],
        'รายละเอียด' : dataset[:counter],
        'คำตอบ' : ansSet
    })
    df_set.to_csv(f"Result_log/{model_name.replace(":", "-")}_{nows}.csv", index=False, encoding='utf-8-sig')
    print('\nExported to '+ model_name.replace(":", "-") + '_' + nows + '.csv')
    '''

#End readFile def


def generate_ollama(syst_prompt: str, prompt: str) -> str:
    """Send a prompt to Ollama and return the generated text."""
    payload = {
        "model": model_name,
        "messages" : [
            { "role": "user", "content": prompt },
            { "role": "system", "content": syst_prompt }
        ],
        "stream": True,          # we want a streaming response like OpenAI
        "max_tokens": 8192,       # optional – adjust as needed
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
                chunk = json.loads(json_part.decode("utf-8"))
                # The text chunk is usually under `response` -> "message" -> "content"
                chunk_text = chunk.get("message", {}).get("content", "")
                print(chunk_text, end="", flush=True)
                generated += chunk_text
    print("\n")
    return generated
#End def


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
#End def


def prepare_facts(step1_json: dict, step2_json: dict) -> dict:
    # 1. Merge ทั้งสอง JSON
    raw_facts = {**step1_json, **step2_json}
    
    # 2. Map หรือ Map Nested Path ให้ตรงกับ KB fact_path (Dot Notation)
    normalized_facts = {
        "event": {
            "patient_received_drug": raw_facts.get("patient_received_drug", "unknown"),
            "harm_occurred": raw_facts.get("harm_occurred", "unknown"),
            "severity": raw_facts.get("severity", "unknown")
        },
        "drug": {
            "intended_drug": raw_facts.get("intended_drug", "unknown"),
            "actual_drug": raw_facts.get("actual_drug", "unknown"),
            "high_alert_drug": raw_facts.get("is_high_alert_drug", "unknown"),
            "is_concentrated_potassium": "potassium" in str(raw_facts.get("intended_drug", "")).lower() or "kcl" in str(raw_facts.get("intended_drug", "")).lower()
        },
        "error": {
            "occurred": raw_facts.get("error_stage") != "unknown",
            "stage": raw_facts.get("error_stage", "unknown"),
            "is_product_selection_error": raw_facts.get("is_product_selection_error", "unknown")
        },
        "medication_reconciliation": {
            "involved": raw_facts.get("med_rec_involved", "unknown"),
            "failure": raw_facts.get("med_rec_failure", "unknown"),
            "omission": raw_facts.get("med_rec_omission", "unknown"),
            "interaction_due_to_med_rec": raw_facts.get("med_rec_interaction", "unknown")
        },
        "interaction": {
            "ddi_present": raw_facts.get("ddi_present", "unknown"),
            "severity": raw_facts.get("ddi_severity", "unknown")
        }
    }
    
    print(normalized_facts)
    return normalized_facts



def evaluate_condition(condition, extracted_facts):
    # ดึงค่าจาก Dot Notation เช่น "drug.high_alert_drug"
    path_parts = condition["fact_path"].split(".")
    val = extracted_facts
    for part in path_parts:
        val = val.get(part, "unknown") if isinstance(val, dict) else "unknown"

    op = condition["operator"]
    target = condition["value"]

    if op == "equals":
        return val == target
    elif op == "in":
        return val in target
    elif op == "not_equals":
        return val != target and val != "unknown"
    return False
#End evaluate_condition


def match_cpm(kbs, extracted_facts):
    kb = json.loads(kbs)
    matched_cpms = []

    for rule in kb["rules"]:
        conds = rule["conditions"]

        # Check all_of
        all_passed = all(
            evaluate_condition(c, extracted_facts)
            for c in conds.get("all_of", [])
        )

        # Check none_of
        none_passed = not any(
            evaluate_condition(c, extracted_facts)
            for c in conds.get("none_of", [])
        )

        if all_passed and none_passed:
            matched_cpms.append(rule)

    # กรอง CPM ที่โดน Override ออก
    override_set = set()
    for rule in matched_cpms:
        override_set.update(rule.get("overrides", []))

    final_cpms = [r for r in matched_cpms if r["cpm_id"] not in override_set]

    # จัดเรียงตาม Priority จากสูงไปต่ำ
    final_cpms.sort(key=lambda x: x["priority"], reverse=True)

    return final_cpms
#End match_cpm


# ----------------------------------------------------------------------
# Example usage – same prompt as before
# ----------------------------------------------------------------------
if __name__ == "__main__":
    #stream_text = generate_ollama( input("\nAsk anything:") )
    readPrompt()
    readFile()

    #extracted_facts = {'event': {'patient_received_drug': True, 'harm_occurred': 'unknown'}, 'drug': {'intended_drug': 'Vit.B6', 'actual_drug': 'Vit.B12', 'high_alert_drug': False, 'is_concentrated_potassium': False}, 'error': {'occurred': True, 'stage': 'dispensing', 'is_product_selection_error': True}, 'medication_reconciliation': {'involved': True, 'failure': True, 'omission': False, 'interaction_due_to_med_rec': False}, 'interaction': {'ddi_present': False, 'severity': 'unknown'}}
    #print(match_cpm(cpm_knowledge_base, extracted_facts))

    # If you need a final newline or any post‑processing, do it here.
#End main
