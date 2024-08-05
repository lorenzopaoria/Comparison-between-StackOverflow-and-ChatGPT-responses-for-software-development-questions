import json
import os
from openai import OpenAI

api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_openai_a(file_path):
    with open(file_path, 'r') as f:
        input_json = json.load(f)
        
    question = input_json[0]['Question']

    try:
        chat_completion = client.chat.completions.create(
            messages=[{ "role": "user", "content": question,}],
            model="gpt-3.5-turbo",
        )

        answer_text = chat_completion.choices[0].message.content.strip()
        return answer_text

    except Exception as e:
        raise Exception(f"Error in getting OpenAI response: {e}")

def openai_a(file_path, answer):
    with open(file_path, 'r') as f:
        input_json = json.load(f)
    
    question_data = input_json[0]
    question_id = question_data['ID']
    question_text = question_data['Question']
    
    base, ext = os.path.splitext(file_path)
    output_file_path = f"{base}_openai_answer{ext}"
    
    output_json = [{
        "ID": question_id,
        "Question": question_text,
        "Answer": answer.replace("\n", " ")
    }]
    
    with open(output_file_path, 'w') as f:
        json.dump(output_json, f, indent=4)

def main():
    file_path_q_without_a = 'q_without_a/q_without_a.json'
    openai_answer = get_openai_a(file_path_q_without_a)
    
    # Answer for questions without answer by chatGpt
    openai_a(file_path_q_without_a, openai_answer)

    #ChatGpt answer for question with codes
    # per ogni domanda di stack presente su  a_with_codes ricavare la risposta di chatgpt e vedere se compila quella di chatgpt e quella di stackoverflow e chiedere a chatgpt se sono similari

    print(f"Risposte scritte per le domande senza risposte in: {file_path_q_without_a}")

if __name__ == '__main__':
    main()
