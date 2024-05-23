import requests
import re
from bs4 import BeautifulSoup #per pulire html dai tag

api_key='0KiuSiLt17YlovAZzROW)Q(('

"""proxies = {
    'http': 'http:google.com:8080',
    'https': 'http:google.com:8080'
}"""

def get_tor_session():
    session= requests.session()
    #tor use port 9050
    session.proxies={ 'http':'socks5://127.0.0.1:9050',
                    'https':'socks5://127.0.0.1:9050'}
    return session

def extract_question_id(url):

    match = re.search(r'questions/(\d+)', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Stack Overflow URL")

def clean_html(raw_html):
    clean_text = BeautifulSoup(raw_html, "html.parser")#,exclude_encodings=["ISO-8859-7"]
    return clean_text.get_text()

def get_question_and_best_answer(question_id, api_key):

    session= requests.session()
    question_url = f'https://api.stackexchange.com/2.3/questions/{question_id}?order=desc&sort=activity&site=stackoverflow&filter=withbody&key={api_key}'
    #question_response = requests.get(question_url,proxies=proxies)
    #question_response = requests.get(question_url)
    question_response = session.get(question_url)
    question_data = question_response.json()

    if not question_data['items']:
        raise ValueError("Question not found")

    question_title = question_data['items'][0]['title']
    question_body = clean_html(question_data['items'][0].get('body', 'No body content'))

    answers_url = f'https://api.stackexchange.com/2.3/questions/{question_id}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody&key={api_key}'
    #answers_response = requests.get(answers_url,proxies=proxies)
    #answers_response = requests.get(answers_url)
    answers_response = session.get(answers_url)
    answers_data = answers_response.json()

    if not answers_data['items']:
        return question_title, question_body, None

    best_answer = None
    for answer in answers_data['items']:
        if answer.get('is_accepted'):
            best_answer = clean_html(answer.get('body', 'No body content'))
            break
    if not best_answer:
        best_answer = clean_html(answers_data['items'][0].get('body', 'No body content'))

    return question_title, question_body, best_answer

def main():
    url = input("Inserisci l'URL della discussione su Stack Overflow: ")

    try:
        question_id = extract_question_id(url)
        question_title, question_body, best_answer = get_question_and_best_answer(question_id, api_key)

        with open('Question_BestAnswer.txt', 'w', encoding='utf-8') as file:
            file.write(f"Titolo della domanda: {question_title}\n")
            file.write(f"Corpo della domanda: {question_body}\n")
            if best_answer:
                file.write(f"Migliore risposta: {best_answer}\n")
            else:
                file.write("Non ci sono risposte alla domanda.")

    except ValueError:
        with open('Question_BestAnswer.txt', 'w', encoding='utf-8') as file:
            file.write('errore nella creazione/scrittura nel Question_BestAnswer.txt')

if __name__ == '__main__':
    main()




