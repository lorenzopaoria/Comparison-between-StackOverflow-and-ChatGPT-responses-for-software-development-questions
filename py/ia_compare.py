import json
import os
from openai import OpenAI

api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# pass to chatGpt the question for receive the answer
def openai_a(question):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{ "role": "user", "content": question }],
            model="gpt-3.5-turbo",
        )

        answer_text = chat_completion.choices[0].message.content.strip()
        return answer_text

    except Exception as e:
        raise Exception(f"Error in getting OpenAI response: {e}")

def write_on_json(file_path, questions_and_answers):
    base, ext = os.path.splitext(file_path)  # for creating a new JSON file
    output_file_path = f"{base}_openai_answer{ext}"
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(questions_and_answers, f, indent=4)

def process_questions(file_path, limit=None):
    with open(file_path, 'r', encoding='utf-8') as f:
        input_json = json.load(f)

    questions_and_answers = []

    num_limit_questions=min(limit if limit is not None else len(input_json), len(input_json))

    for i, item in enumerate(input_json):
        if i >= num_limit_questions: break

        if 'Question' in item:
            question_id = item.get('ID', 'unknown')
            question_text = item['Question']
            
            answer = openai_a(question_text)
            best_answer = item.get('Best Answer', None)
            
            output_json = {"ID": question_id, "Question": question_text, "ChatGpt answer": answer.replace("\n", " ")}
            
            if best_answer is not None:
                output_json["Stack Overflow best answer"] = best_answer
            
            questions_and_answers.append(output_json)

    write_on_json(file_path, questions_and_answers)

def main():
    file_path_q_without_a = 'q_without_a/q_without_a.json'
    file_path_short_q= 'q_shorter_than/short_q.json'
    
    # Answer for questions without answer by chatGpt
    process_questions(file_path_q_without_a, limit=5)

    #ChatGpt answer for question with codes
    # per ogni domanda di stack presente su  a_with_codes ricavare la risposta di chatgpt e vedere se compila quella di chatgpt e quella di stackoverflow e chiedere a chatgpt se sono similari

    # Answer for short question by chatGpt
    process_questions(file_path_short_q, limit=5)

    print(f"Risposte scritte per le domande senza risposte in: {file_path_q_without_a}")
    print(f"Risposte scritte per le domande sotto i 700 caratteri: {file_path_q_without_a}")


if __name__ == '__main__':
    main()
