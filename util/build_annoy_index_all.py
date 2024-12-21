import os
import pandas as pd
from annoy import AnnoyIndex
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from util.database import engine
from config.constants import LocalPath

def build_annoy_index():
    # artifacts 경로가 없으면 생성
    os.makedirs(LocalPath.ARTIFACTS, exist_ok=True)

    with engine.connect() as connection:
        df = pd.read_sql_table('TbKaMessage', con=connection)

    # TF-IDF 벡터화
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['message']).toarray()

    # Annoy 인덱스 생성
    f = tfidf_matrix.shape[1]  # 벡터의 차원
    annoy_index = AnnoyIndex(f, 'angular')

    # 각 벡터를 Annoy 인덱스에 추가
    for i, vector in enumerate(tfidf_matrix):
        annoy_index.add_item(i, vector)

    annoy_index.build(n_trees=10)
    annoy_index.save(LocalPath.ANNOY_INDEX_ALL)

    # TF-IDF 벡터화 모델 저장
    with open(LocalPath.TFIDF_VECTORIZER_ALL, 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)
