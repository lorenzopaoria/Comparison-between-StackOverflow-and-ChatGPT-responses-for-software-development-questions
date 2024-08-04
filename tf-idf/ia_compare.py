import requests
import json
import os

def get_openai_a(file_path, api_key):
    with open(file_path, 'r') as f:
        input_json = json.load(f)
        
    question = input_json[0]['Question']

    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-4',
        'messages': [
            {'role': 'user', 'content': question}
        ],
        'max_tokens': 150,
        'temperature': 0.7
    }

    answer = requests.post(url, headers=headers, json=data)

    if answer.status_code == 200:
        answer_text = answer.json()
        return answer_text['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"Errore")

def openai_a(file_path, answer):
    with open(file_path, 'r') as f:
        input_json = json.load(f)
    
    question_data = input_json[0]
    question_id = question_data['ID']
    question_text = question_data['Question']
    
    base, ext = os.path.splitext(file_path)
    output_file_path = f"{base}_openai_answer{ext}"
    
    output_json = {
        "ID": question_id,
        "Question": question_text,
        "Answer": answer.replace("\n", " ")
    }
    
    with open(output_file_path, 'w') as f:
        json.dump(output_json, f, indent=4)

def main():
    file_path = 'q_without_a/q_without_a.json'
    api_key = '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'

    openai_answer = get_openai_a(file_path, api_key)
    
    #Answer for questions without answer by chatGpt
    openai_a(file_path, openai_answer)
    
    print(f"Risposte scritte per le domande senza risposte in:{file_path}")

if __name__ == '__main__':
    main()
