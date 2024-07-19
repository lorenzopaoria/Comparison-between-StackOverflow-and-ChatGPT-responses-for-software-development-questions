import nltk
import pandas as pd
from lxml import etree
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text
from nltk.corpus import stopwords

file_path = 'Posts.xml'

def extract_posts(file_path, limit=None):
    questions = []
    best_answers = {}
    unanswered_questions = []
    with open(file_path, 'rb') as f:
        context = etree.iterparse(f, events=('end',), tag='row')
        for i, (event, elem) in enumerate(context):
            post_id = elem.get('Id')
            post_type = elem.get('PostTypeId')  # 1=Question, 2=Answer
            body = elem.get('Body')
            score = int(elem.get('Score'))
            parent_id = elem.get('ParentId')

            if post_type == '1':
                cleaned_body = BeautifulSoup(body, 'html.parser').get_text()
                questions.append((post_id, cleaned_body))
            elif post_type == '2' and parent_id:
                if parent_id not in best_answers or score > best_answers[parent_id][1]:
                    cleaned_body = BeautifulSoup(body, 'html.parser').get_text()
                    best_answers[parent_id] = (cleaned_body, score)

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            if limit and i >= limit - 1:
                break

    for qid, question in questions:
        if qid not in best_answers:
            unanswered_questions.append((qid, question))

    return questions, best_answers, unanswered_questions

questions, best_answers, unanswered_questions = extract_posts(file_path, limit=1000)

answered_questions = [(qid, question) for qid, question in questions if qid in best_answers]
posts = [q[1] for q in answered_questions] + [best_answers[qid][0] for qid in best_answers]

nltk.download('stopwords')
stop_words_nltk=set(stopwords.words('english'))
added_stopwords=text.ENGLISH_STOP_WORDS.union(stop_words_nltk)

vectorizer = TfidfVectorizer(max_df=0.8, min_df=3, stop_words=list(added_stopwords))

tfidf_matrix = vectorizer.fit_transform(posts)

feature_names = vectorizer.get_feature_names_out()

dense_tfidf_matrix = tfidf_matrix.todense()

df_tfidf = pd.DataFrame(dense_tfidf_matrix, columns=feature_names)

output_file_path = 'tfidf_results.txt'

with open(output_file_path, 'w', encoding='utf-8') as f:
    for i, (qid, question) in enumerate(answered_questions):
        f.write(f"Question {qid}:\n") #id of question are not progessive number
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

with open('questions_without_answers.txt', 'w', encoding='utf-8') as f:
    for qid, question in unanswered_questions:
        f.write(f"Question {qid}:\n")
        f.write(question + "\n\n")
        f.write("-" * 100 + "\n\n")

print(f'Le domande con le risposte sono state salvate nel file: {output_file_path}')
print(f'Le domande senza risposte sono state salvate nel file: questions_without_answers.txt')
