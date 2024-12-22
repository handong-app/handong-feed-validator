import os
import pandas as pd
from annoy import AnnoyIndex
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import text
import pickle
from util.database import engine
from config.constants import LocalPath, DatabaseConfig

def build_annoy_index_last_14days():
    # artifacts 경로가 없으면 생성
    os.makedirs(LocalPath.ARTIFACTS, exist_ok=True)

    #  최근 14일 데이터만 조회
    with engine.connect() as connection:
        query = text(DatabaseConfig.GET_TbKaMessage_LAST_14DAYS)
        df = pd.read_sql(query, con=connection)

    # 데이터가 없으면 중단
    if df.empty:
        raise ValueError("No data available from the last 14 days to build artifacts.")

    # TF-IDF 벡터화
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['message']).toarray()

    # Annoy 인덱스 생성
    f = tfidf_matrix.shape[1]  # 열의 개수, 벡터의 차원 (Vectorizer가 생성한 어휘의 고유 단어 개수와 동일)
    annoy_index = AnnoyIndex(f, 'angular')

    # 각 벡터를 Annoy 인덱스에 추가
    for i, vector in enumerate(tfidf_matrix):
        annoy_index.add_item(i, vector)

    annoy_index.build(n_trees=10)
    annoy_index.save(LocalPath.ANNOY_INDEX_LAST_14DAYS)

    # TF-IDF 벡터화 모델 저장
    with open(LocalPath.TFIDF_VECTORIZER_LAST_14DAYS, 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)

    # 데이터 프레임 저장
    with open(LocalPath.LAST_14DAYS_DF, 'wb') as f:
        pickle.dump(df, f)