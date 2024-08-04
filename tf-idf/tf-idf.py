import nltk 
import pandas as pd
import json 
import os
from lxml import etree #xml
from bs4 import BeautifulSoup #clean the html 
from sklearn.feature_extraction.text import TfidfVectorizer #tfidfVectorizer algorithm
from sklearn.feature_extraction import text #stopwords
from nltk.corpus import stopwords #stopwords 

file_path = 'stackOverflowDump/Posts.xml'

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

def write_to_json(file_path, genetate_func, *args):
    data=  genetate_func(*args)
    with open(file_path, 'w', encoding= 'utf-8') as f:
        json.dump(data, f, ensure_ascii= False, indent= 4)

def generate_tfidf(df_tfidf):
    questions_list= []
    for i, (qid, question, _raw_body) in enumerate(answered_questions):
        question_dict= {
            "ID:":qid,
            "Question": question.replace("\n", " "),
            "TF-IDF scores": []
        }
        tfidf_scores = df_tfidf.iloc[i]
        max_score = tfidf_scores.max()
        max_term = tfidf_scores.idxmax()
        tfidf_scores_dict= {word: score for word, score in tfidf_scores.items() if score > 0}
        question_dict["TF-IDF scores"].append({
            "Scores": tfidf_scores_dict,
            "Max term": max_term,
            "Max score": max_score
        })

        best_answer_index = len(answered_questions) + list(best_answers.keys()).index(qid)
        best_answer = best_answers[qid][0]

        best_answer_tfidf_scores = df_tfidf.iloc[best_answer_index]
        best_answer_max_score = best_answer_tfidf_scores.max()
        best_answer_max_term = best_answer_tfidf_scores.idxmax()
        best_answer_tfidf_scores_dict = {word: score for word, score in best_answer_tfidf_scores.items() if score > 0}

        question_dict["Best Answer"] = best_answer.replace("\n", " ")
        question_dict["Best Answer TF-IDF scores"] = {
            "Scores": best_answer_tfidf_scores_dict,
            "Max term": best_answer_max_term,
            "Max score": best_answer_max_score
        }
        questions_list.append(question_dict)
    
    return questions_list

def generate_q_for_tfidf_terms(df_tfidf, keyword):
    questions_list = []
    for i, (qid, question, _raw_body) in enumerate(answered_questions):
        tfidf_scores = df_tfidf.iloc[i]
        max_term = tfidf_scores.idxmax()
        
        if max_term == keyword or (keyword in tfidf_scores.index and tfidf_scores[keyword] > 0.3):
            question_dict = {
                "ID": qid,
                "Question": question.replace("\n", " "),
                "TF-IDF scores": [],
                "Best answer": "",
                "Best answer TF-IDF scores": []
            }

            max_score = tfidf_scores[max_term]
            tfidf_scores_dict = {word: score for word, score in tfidf_scores.items() if score > 0}
            question_dict["TF-IDF scores"].append({
                "Scores": tfidf_scores_dict,
                "Max term": max_term,
                "Max score": max_score
            })

            best_answer_index = len(answered_questions) + list(best_answers.keys()).index(qid)
            best_answer = best_answers[qid][0]
            question_dict["Best answer"] = best_answer.replace("\n", " ")

            tfidf_scores_best_answer = df_tfidf.iloc[best_answer_index]
            max_term_best_answer = tfidf_scores_best_answer.idxmax()
            max_score_best_answer = tfidf_scores_best_answer[max_term_best_answer]
            best_answer_tfidf_scores_dict = {word: score for word, score in tfidf_scores_best_answer.items() if score > 0}

            question_dict["Best answer TF-IDF scores"].append({
                "Scores": best_answer_tfidf_scores_dict,
                "Max term": max_term_best_answer,
                "Max score": max_score_best_answer
            })
            questions_list.append(question_dict)

    return questions_list

def generate_files_for_keywords(df_tfidf, keywords):
    for keyword in keywords:
        file_path = f"q_for_tfidf_term/q_with_{keyword}.json"
        write_to_json(file_path, generate_q_for_tfidf_terms, df_tfidf, keyword)

def generate_unanswered_q():
    questions_list = []
    for qid, question, _raw_body in unanswered_questions:
        question_dict = {
            "ID": qid,
            "Question": question.replace("\n", " ")
        }
        questions_list.append(question_dict)
    return questions_list

def generate_short_q(limit_char=700):
    question_list=[]
    for qid, question, _raw_body in answered_questions:
        best_answer = best_answers[qid][0]
        if len(question) < limit_char:
            question_dict = {
                "ID:": qid,
                "Question": question.replace("\n"," "),
                "Best Answer": best_answer.replace("\n"," "),
            }
            question_list.append(question_dict)
    return question_list

def generate_a_with_code():
    questions_list = []
    for _i, (qid, question, raw_body) in enumerate(answered_questions):
        best_answer = best_answers[qid][0]
        raw_answer_body = best_answers[qid][2]
        if contains_code(best_answer, raw_answer_body):
            question_dict = {
                "ID": qid,
                "Question": question.replace("\n", " "),
                "Best Answer": best_answer.replace("\n", " ")
            }
            questions_list.append(question_dict)
    return questions_list

def main():

    stopwords_list=added_stopwords_func()
    df_tfidf = create_tfidf_matrix(posts, stopwords_list)
    keywords = ["python", "C++", "java", "php", "html", "sql", "css", "programming"]

    # TF-IDF Results
    write_to_json('tfidf_results/tfidf_results.json', generate_tfidf, df_tfidf)

    # Questions Without Answers
    write_to_json('q_without_a/q_without_a.json', generate_unanswered_q)

    # Questions and Answers Shorter Than a Limit
    write_to_json('q_shorter_than/short_q.json', generate_short_q)

    # Questions and Answers with Code
    write_to_json('qa_with_codes/qa_with_codes.json', generate_a_with_code)

    #Questions with keywords in tf_idf terms
    generate_files_for_keywords(df_tfidf, keywords)

    print(f'Le domande con le risposte sono state salvate in json')
    print(f'Le domande senza risposte sono state salvate in json')
    print(f'Le domande sotto i 700 caratteri sono state salvate in json')
    print(f'Le domande e le risposte contenenti codice sono state salvate in json')
    print(f'Le domande contenenti tf_idf keywords sono state salvate in json')

if __name__ == "__main__":
    main()