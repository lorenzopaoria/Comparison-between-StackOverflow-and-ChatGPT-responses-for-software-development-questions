import nltk 
import pandas as pd
import json 
import os
from lxml import etree #xml
from bs4 import BeautifulSoup #clean the html 
from sklearn.feature_extraction.text import TfidfVectorizer #tfidfVectorizer algorithm
from sklearn.feature_extraction import text #stopwords
from nltk.corpus import stopwords #stopwords 

file_path = 'Posts.xml'

QUESTION = '1' # 1=Question, 2=Answer
ANSWER = '2'

def extract_posts(file_path, limit=None):
    questions = []
    best_answers = {}
    unanswered_questions = []
    with open(file_path, 'rb') as f:
        context = etree.iterparse(f, events=('end',), tag='row')
        for i, (_event, elem) in enumerate(context):
            post_id = elem.get('Id') #is not a progressive number for question
            post_type = elem.get('PostTypeId')  
            body = elem.get('Body')
            score = int(elem.get('Score'))
            parent_id = elem.get('ParentId')
            cleaned_body = BeautifulSoup(body, 'html.parser').get_text()

            if post_type == QUESTION :
                questions.append((post_id, cleaned_body, body))
            elif post_type == ANSWER and parent_id:
                if parent_id not in best_answers or score > best_answers[parent_id][1]: #the best answer have the max score
                    best_answers[parent_id] = (cleaned_body, score, body)

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            if limit and i >= limit - 1: #limit use for fast result
                break

    for qid, question, raw_body in questions: #a question may not have an answer
        if qid not in best_answers:
            unanswered_questions.append((qid, question, raw_body))

    return questions, best_answers, unanswered_questions

def contains_code(_text, raw_body):
    soup=BeautifulSoup(raw_body, 'html.parser')
    code_tags=soup.find_all(['code', 'pre']) #tag html for codes
    return bool(code_tags) #if the list is full the bool return 1

def added_stopwords_func():
    stopwords_file = 'stopwords.json'

    if os.path.exists(stopwords_file): #if the stopwords file exist open it 
        with open(stopwords_file, 'r') as file:
            added_stopwords = json.load(file)
    else: #if doesn't exist download the package
        nltk.download('stopwords')
        stop_words_nltk = set(stopwords.words('english'))
        
        added_stopwords = list(text.ENGLISH_STOP_WORDS.union(stop_words_nltk)) #union between nltk stopwords and sklearn stopwords

        with open(stopwords_file, 'w') as file:
            json.dump(added_stopwords, file) #save the file for the next time
    
    return added_stopwords

questions, best_answers, unanswered_questions = extract_posts(file_path, limit=1000) 

answered_questions = [(qid, question, raw_body) for qid, question, raw_body in questions if qid in best_answers] #creation of a list with associate answer

posts = [q[1] for q in answered_questions] + [best_answers[qid][0] for qid in best_answers] #creation of a list which have in q[1] the cleaned body of the answered_question and in [qid][0] the best answer with cleaned body

def create_tfidf_matrix(posts, stopwords_list, max_df=0.8, min_df=3):
    vectorizer = TfidfVectorizer(max_df=max_df, min_df=min_df, stop_words=stopwords_list)

    tfidf_matrix = vectorizer.fit_transform(posts)
    feature_names = vectorizer.get_feature_names_out()
    dense_tfidf_matrix = tfidf_matrix.todense()
    df_tfidf = pd.DataFrame(dense_tfidf_matrix, columns=feature_names)
    
    return df_tfidf

def write_to_file(file_path, generate_func, *args): 
    with open(file_path, 'w', encoding='utf-8') as f:
        generate_func(f, *args)

def generate_tfidf(f,df_tfidf):
    for i, (qid, question, _raw_body) in enumerate(answered_questions):
        f.write(f"Question {qid}:\n")
        f.write(question + "\n\n")
        f.write("TF-IDF Scores:\n")
        tfidf_scores = df_tfidf.iloc[i]
        max_score = tfidf_scores.max()
        max_term = tfidf_scores.idxmax()
        for word, score in tfidf_scores.items():
            if score > 0:
                f.write(f"{word}: {score:.4f}\n")
        f.write(f"\nTermine con il punteggio TF-IDF più alto: {max_term} ({max_score:.4f})\n")

        f.write("\nBest Answer:\n")
        best_answer_index = len(answered_questions) + list(best_answers.keys()).index(qid)
        best_answer = best_answers[qid][0]
        f.write(best_answer + "\n\n")
        f.write("TF-IDF Scores:\n")
        tfidf_scores = df_tfidf.iloc[best_answer_index]
        max_score = tfidf_scores.max()
        max_term = tfidf_scores.idxmax()
        for word, score in tfidf_scores.items():
            if score > 0:
                f.write(f"{word}: {score:.4f}\n")
        f.write(f"\nTermine con il punteggio TF-IDF più alto: {max_term} ({max_score:.4f})\n")
        f.write("\n" + "-"*100 + "\n\n")

def generate_unanswered_questions(f):
    for qid, question, _raw_body in unanswered_questions:
        f.write(f"Question {qid}:\n")
        f.write(question + "\n\n")
        f.write("-" * 100 + "\n\n")

def generate_short_qa(f, limit_char=700):
    for qid, question, _raw_body in answered_questions:
        best_answer = best_answers[qid][0]
        if len(best_answer) < limit_char and len(question) < limit_char:
            f.write(f"Question {qid}:\n")
            f.write(question + "\n\n")
            f.write("Best Answer:\n")
            f.write(best_answer + "\n\n")
            f.write("-" * 100 + "\n\n")

def generate_qa_with_code(f):
    for _i, (qid, question, raw_body) in enumerate(answered_questions):
        best_answer = best_answers[qid][0]
        raw_answer_body = best_answers[qid][2]
        if contains_code(question, raw_body) or contains_code(best_answer, raw_answer_body):
            f.write(f"Question {qid}:\n")
            f.write(question + "\n\n")
            f.write("Best Answer:\n")
            f.write(best_answer + "\n\n")
            f.write("-" * 100 + "\n\n")

#NOTA: classificare le domande tramite tf-idf term

def main():

    stopwords_list=added_stopwords_func()
    df_tfidf = create_tfidf_matrix(posts, stopwords_list)

    # TF-IDF Results
    write_to_file('tfidf_results.txt', generate_tfidf, df_tfidf)

    # Questions Without Answers
    write_to_file('q_without_a.txt', generate_unanswered_questions)

    # Questions and Answers Shorter Than a Limit
    write_to_file('short_qa.txt', generate_short_qa)

    # Questions and Answers with Code
    write_to_file('qa_with_codes.txt', generate_qa_with_code)

    #nota: aggiungere catalogazioni per tfidf

    print(f'Le domande con le risposte sono state salvate')
    print(f'Le domande senza risposte sono state salvate')
    print(f'Le domande e le risposte sotto i 200 caratteri sono state salvate')
    print(f'Le domande e le risposte contenenti codice sono state salvate')

if __name__ == "__main__":
    main()