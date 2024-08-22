import json 
import os
import time # timer
from openai import OpenAI # request openai
from concurrent.futures import ThreadPoolExecutor # pool of thread
import functools # cache for function

api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#data for gpt-4o-mini acccording to site: https://platform.openai.com/settings/organization/limits
RATE_LIMIT_TPM = 200000  # max 200,000 tokens per minute
RATE_LIMIT_BUFFER = 5000  # buffer to avoid hitting the exact limit
TOKEN_COST_PER_REQUEST = 2000  # estimated token cost per request 

tokens_used = 0

start_time = time.time()

# get ai answer witch caching for redundant questions
@functools.lru_cache(maxsize = None)
def ai_answer(question, code = False):
    global tokens_used, start_time

    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time < 60:
        if tokens_used + TOKEN_COST_PER_REQUEST >= RATE_LIMIT_TPM - RATE_LIMIT_BUFFER:
            sleep_time = 60 - elapsed_time
            time.sleep(sleep_time)
            tokens_used = 0
            start_time = time.time()
    else:
        tokens_used = 0
        start_time = current_time

    try:
        if code:
            modified_question = question + " if there is code in the question, answer with code if needed." 
        else: modified_question = question
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": modified_question}],
            model="gpt-4o-mini",
        )
        answer_text = chat_completion.choices[0].message.content.strip()

        tokens_used += TOKEN_COST_PER_REQUEST 

        return answer_text
    except Exception as e:
        raise Exception(f"Error in getting OpenAI response: {e}")

# write answer on json
def write_on_json(file_path, questions_and_answers):
    output_file_path = f"{os.path.splitext(file_path)[0]}_openai_answer.json"
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(questions_and_answers, f, indent=4)

# compare ai answer with so answer
def compare_answers(chatgpt_answer, best_answer):
    comparison_question = f"Are the following two answers equivalent? Say yes or no.\nAnswer 1: {chatgpt_answer}\nAnswer 2: {best_answer}"
    return ai_answer(comparison_question, False)

# check if the code compile
def code_compiling(question, chatgpt_answer, best_answer):
    compile_question = (
        "Say if there is code or not in the question and in the two answers, and then say if the code compiles "
        "(i.e., if it's semantically correct) or not for the question and for the two answers. "
        "If there is no code, the output should be 'code: No, compile: N/A'. "
        "If there is code, the output should either be 'code: Yes, compile: Yes' or 'code: Yes, compile: No'. "
        "Note that 'code: Yes, compile: N/A' is not an acceptable output.\n\n"
        "Output format should be:\n"
        "Question: code: Yes/No, compile: Yes/No/N/A;\n"
        "Answer StackOverflow: code: Yes/No, compile: Yes/No/N/A;\n"
        "Answer ChatGpt: code: Yes/No, compile: Yes/No/N/A.\n\n"
        f"Question: {question}\n"
        f"Answer StackOverflow: {best_answer}\n"
        f"Answer ChatGpt: {chatgpt_answer}"
    )
    return ai_answer(compile_question, True)

# process questions from a json
def process_questions(file_path, limit = None, comparison = False, code_comp = False):
    with open(file_path, 'r', encoding = 'utf-8') as f:
        input_json = json.load(f)

    questions_and_answers = []
    num_limit_questions = min(limit if limit is not None else len(input_json), len(input_json))

    def process_item(i, item):
        if i >= num_limit_questions:
            return None

        if 'Question' in item:
            question_id = item.get('ID', 'unknown')
            question_text = item['Question']

            try:
                answer = ai_answer(question_text)
                best_answer = item.get('Best answer', None)

                output_json = {"ID": question_id, "Question": question_text, "ChatGpt answer": answer.replace("\n", " ")}

                if best_answer is not None:
                    output_json["Stack Overflow best answer"] = best_answer

                    if comparison:
                        comparison_result = compare_answers(answer, best_answer)
                        output_json["Are the two answers equivalent?"] = comparison_result.replace("\n", " ")

                    if code_comp:
                        code_comp_result = code_compiling(question_text, answer, best_answer)
                        code_compile_info = {
                            "Question": {"code": "No", "compile": "No"},
                            "Answer StackOverflow": {"code": "No", "compile": "No"},
                            "Answer ChatGpt": {"code": "No", "compile": "No"},
                        }

                        result_parts = code_comp_result.split(';')
                        for part in result_parts:
                            if ':' in part:
                                key, values = part.split(':', 1)
                                key = key.strip()
                                sub_results = values.split(',')
                                for sub_result in sub_results:
                                    if ':' in sub_result:
                                        sub_key, sub_value = sub_result.split(':', 1)
                                        sub_key = sub_key.strip()
                                        sub_value = sub_value.strip()
                                        if key in code_compile_info:
                                            code_compile_info[key][sub_key] = sub_value

                        output_json["Code and Compile Information"] = code_compile_info

                return output_json

            except Exception as e:
                print(f"Skipping question due to error: {e}")
                return None

    # API request parallelized
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda x: process_item(x[0], x[1]), enumerate(input_json)))

    questions_and_answers = [result for result in results if result]
    write_on_json(file_path, questions_and_answers)

# process question form a json in a directory
def process_questions_in_directory(directory_path, limit = None, comparison = False, code_comp = False):
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.json') and 'openai' not in file_name:
            file_path = os.path.join(directory_path, file_name)
            process_questions(file_path, limit, comparison, code_comp)

def main():
    file_path_q_without_a = 'q_without_a/q_without_a.json'
    file_path_short_q = 'q_shorter_than/short_q.json'
    file_path_long_q = 'q_longer_than/long_q.json'
    file_path_qa_with_code = 'qa_with_codes/qa_with_codes.json'
    directory_path_q_tfidf_terms = 'q_for_tfidf_term/'

    process_questions(file_path_q_without_a, limit = None, comparison = False, code_comp = False)
    print("Answers written for questions without answers in JSON")

    process_questions(file_path_qa_with_code, limit = None, comparison = True, code_comp = True)
    print("Answers written for questions and answers with code in JSON")

    process_questions(file_path_short_q, limit = None, comparison = True, code_comp = False)
    print("Answers written for questions shorter than 700 characters in JSON")

    process_questions(file_path_long_q, limit = None, comparison = True, code_comp = False)
    print("Answers written for questions longer than 700 characters in JSON")

    process_questions_in_directory(directory_path_q_tfidf_terms, limit = None, comparison = True, code_comp = False)
    print("Answers written for questions with specific TF-IDF terms in JSON")

if __name__ == '__main__':
    main()
