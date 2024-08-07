import json
import os
from openai import OpenAI

api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# pass to chatGpt the question for receive the answer
def ai_answer(question):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{ "role": "user", "content": question }],
            model="gpt-3.5-turbo",
        )
        answer_text = chat_completion.choices[0].message.content.strip()
        return answer_text

    except Exception as e:
        raise Exception(f"Error in getting OpenAI response: {e}")

# create a json with custom name
def write_on_json(file_path, questions_and_answers):
    base, ext = os.path.splitext(file_path)  # for creating a new JSON file
    output_file_path = f"{base}_openai_answer{ext}"
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(questions_and_answers, f, indent=4)

# ask to chatGpt if the two answers are equivalent
def compare_answers(chatgpt_answer, best_answer):
    comparison_question = f"Are the following two answers equivalent?, say yes or no.\nAnswer 1: {chatgpt_answer}\nAnswer 2: {best_answer}"
    comparison_response = ai_answer(comparison_question)
    return comparison_response

#ask to chatGpt if the code provided in question and answer compile
#strutturare la risposta per il compiling in modo tale da semplificare il lavoro per l'analisi dei risultati
def code_compiling(question, chatgpt_answer, best_answer):
    compile_question = f"Say if there is code or not in: question and in the two answers, and say if the code compile or not for the question and for the two answers.\nQuestion: {question}\nAnswer 1: {chatgpt_answer}\nAnswer 2: {best_answer}, outline: Question - code: yes/no, compile: yes/no, Answer 1 - code: yes/no, compile: yes/no, Answer 2 - code: yes/no, compile: yes/no"
    compile_response = ai_answer(compile_question)
    return compile_response

# read the input json for setting up the output json
def process_questions(file_path, limit= None, comparison= False, code_comp= False):
    with open(file_path, 'r', encoding='utf-8') as f:
        input_json = json.load(f)

    questions_and_answers = []

    num_limit_questions=min(limit if limit is not None else len(input_json), len(input_json))# for fast result

    for i, item in enumerate(input_json):
        if i >= num_limit_questions: break

        if 'Question' in item:
            question_id = item.get('ID', 'unknown')
            question_text = item['Question']
            
            answer = ai_answer(question_text)
            best_answer = item.get('Best answer', None)
            
            output_json = {"ID": question_id, "Question": question_text, "ChatGpt answer": answer.replace("\n", " ")}
            
            if best_answer is not None:
                output_json["Stack Overflow best answer"] = best_answer

                if comparison:
                    comparison_result = compare_answers(answer, best_answer)
                    output_json["Are the two answers equivalent?"] = comparison_result.replace("\n", " ")

                if code_comp:
                    code_comp_result =  code_compiling(question_text, answer, best_answer)
                    output_json["Are the code in the Question and in the Answers compile code?"] = code_comp_result.replace("\n", " ")
            
            questions_and_answers.append(output_json)

    write_on_json(file_path, questions_and_answers)

def process_questions_in_directory(directory_path, limit= None, comparison= False, code_comp= False):
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.json') and 'openai' not in file_name:# to ensure that the output file from the first run of the program is not used
            file_path = os.path.join(directory_path, file_name)
            process_questions(file_path, limit, comparison, code_comp)

def main():
    file_path_q_without_a = 'q_without_a/q_without_a.json'
    file_path_short_q= 'q_shorter_than/short_q.json'
    file_path_a_with_code= 'qa_with_codes/qa_with_codes.json'
    directory_path_q_tfidf_terms= 'q_for_tfidf_term/'
    
    # Answer by chatGpt for questions without answer
    process_questions(file_path_q_without_a, limit=5, comparison= False, code_comp= False)
    #ChatGpt answer for question with codes
    process_questions(file_path_a_with_code, limit= 5, comparison= True, code_comp= True)
    # Answer for short question by chatGpt
    process_questions(file_path_short_q, limit=5, comparison= True, code_comp= False)
    # Answer for tf-idf terms
    process_questions_in_directory(directory_path_q_tfidf_terms, limit= 5, comparison= True, code_comp= False)

    print(f"Risposte scritte per le domande senza risposte in json")
    print(f"Risposte scritte per le domande sotto i 700 caratteri e scritte equivalenze in json")
    print(f"Risposte scritte per le domande e risposte col codice, scritte equivalenze, scritti risultati compilazione in json")
    print(f"Risposte scritte per le domande con specifici tfidf terms in json")

if __name__ == '__main__':
    main()
