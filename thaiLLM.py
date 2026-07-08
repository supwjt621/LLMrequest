import requests
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
            "model": "thalle-0.2-thaillm-8b-fa",
            "messages": [ {"role": "user", "content": Question} ],
            "max_tokens": 2048,
            "temperature": 0.3
        }

        response = requests.post(URLs, json=data, headers=headers)

        if response.status_code == 200:
            textResp = response.json()
            finalText = textResp['choices'][0]['message']['content']
            pos = finalText.find('</think>')
            if pos != -1:
                print(finalText[pos+len('</think>')+1:])
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    ContinuePrompt()