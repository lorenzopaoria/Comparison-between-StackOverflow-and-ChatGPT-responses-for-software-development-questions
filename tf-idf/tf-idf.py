import pandas as pd
from lxml import etree
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer

file_path = 'Posts.xml'

def extract_posts(file_path, limit=None):
    posts = []
    with open(file_path, 'rb') as f:
        context = etree.iterparse(f, events=('end',), tag='row')
        for i, (event, elem) in enumerate(context):
            post_type = elem.get('PostTypeId')  # 1=Question, 2=Answer, Answer with max score are the best answer
            body = elem.get('Body')
            score_best_ans= elem.get('Score')
            if post_type == '1':
                cleaned_body = BeautifulSoup(body, 'html.parser').get_text()
                posts.append(cleaned_body)
            elem.clear()
            #if post_type=='2': 
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            if limit and i >= limit - 1:
                break
    return posts

posts = extract_posts(file_path, limit=1000)

#if max_df is 1.0, means "ignore terms that appear in more than 100% of the documents"
#if min_df is 1, means "ignore terms that appear in less than 1 document"
vectorizer = TfidfVectorizer(max_df=0.8, min_df=3, stop_words='english')

tfidf_matrix = vectorizer.fit_transform(posts)

feature_names = vectorizer.get_feature_names_out()

dense_tfidf_matrix = tfidf_matrix.todense()

df_tfidf = pd.DataFrame(dense_tfidf_matrix, columns=feature_names)

output_file_path = 'tfidf_results.txt'

with open(output_file_path, 'w', encoding='utf-8') as f:
    for i, post in enumerate(posts):
        f.write(f"Post {i+1}:\n")
        f.write(post + "\n\n")
        f.write("TF-IDF Scores:\n")
        tfidf_scores = df_tfidf.iloc[i]
        max_score = tfidf_scores.max()
        max_term = tfidf_scores.idxmax()
        for word, score in tfidf_scores.items():
            if score > 0:
                f.write(f"{word}: {score:.4f}\n")
        f.write(f"\nTermine con il punteggio TF-IDF più alto: {max_term} ({max_score:.4f})\n")
        f.write("\n" + "-"*100 + "\n\n")

print(f'I risultati TF-IDF sono stati salvati nel file: {output_file_path}')
