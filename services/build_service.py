import os
import pandas as pd
from annoy import AnnoyIndex
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import text
import pickle
from util.database import engine
from config.constants import LocalPath, DatabaseConfig
from util.io_utils import output_ln


class BuildService:
    @staticmethod
    def build_annoy_index_last_14days():
        # artifacts 경로가 없으면 생성
        os.makedirs(LocalPath.ARTIFACTS, exist_ok=True)

        #  최근 14일 데이터만 조회
        with engine.connect() as connection:
            query = text(DatabaseConfig.GET_TbKaMessage_LAST_14DAYS)
            df = pd.read_sql(query, con=connection)

        if df.empty:
            output_ln("⚠️ [build_annoy_index_last_14days] 지난 14일 동안 데이터가 없음. 빈 아티팩트 생성.")

            # 빈 DataFrame 생성
            df = pd.DataFrame(columns=['id', 'message', 'subject_id', 'created_at'])

            # 빈 TF-IDF 벡터라이저 생성 (더미 데이터 사용, 아예 빈 벡터라이저를 저장하는 것은 불가능함)
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_vectorizer.fit(["dummy"])

            # 빈 Annoy 인덱스 생성
            annoy_index = AnnoyIndex(1, 'angular')

        else:
            # TF-IDF 벡터화
            tfidf_vectorizer = TfidfVectorizer()
            tfidf_matrix = tfidf_vectorizer.fit_transform(df['message']).toarray()

            # Annoy 인덱스 생성
            f = tfidf_matrix.shape[1]  # 벡터 차원
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

    @staticmethod
    def build_annoy_index_all():
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
