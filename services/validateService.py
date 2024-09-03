import math
import uuid
import pickle
from datetime import datetime
from sqlalchemy.orm import Session
from annoy import AnnoyIndex
import pandas as pd

from util.database import engine, db_insert
from schemas.validateRequest import ValidateRequest

class ValidateService:
    @staticmethod
    def process_validate(request: ValidateRequest, session: Session):
        # TF-IDF 벡터화 모델 로드
        with open('artifacts/tfidf_vectorizer.pkl', 'rb') as f:
            tfidf_vectorizer = pickle.load(f)

        # Annoy 인덱스 로드
        f = len(tfidf_vectorizer.get_feature_names_out())
        annoy_index = AnnoyIndex(f, 'angular')
        annoy_index.load('artifacts/annoy_index.ann')

        # 기존 메시지 로드
        with engine.connect() as connection:
            df = pd.read_sql_table('mydb_TbKaFeed', con=connection)

        # 입력된 텍스트 TF-IDF 벡터화
        request_message_vector = tfidf_vectorizer.transform([request.message]).toarray().flatten()

        # 가장 유사한 메시지 검색
        n_similar = 1
        similar_items, distances = annoy_index.get_nns_by_vector(request_message_vector, n_similar, include_distances=True)

        threshold = 1.1

        # for idx in range(len(distances)):
        # 메시지 ID 생성 (UUID)
        message_id = str(uuid.uuid4()).replace('-', '')
        print(message_id)
        # 현재 시간으로 createdDate와 modifiedDate 설정
        current_time = datetime.now()
        print(current_time)

        if distances[0] < threshold:
            print("유사한 항목 인덱스:", similar_items[0])
            print(f"중복된 메시지입니다. (거리: {distances[0]})")
            print(f"유사한 메시지\n\n {df.iloc[similar_items[0]]['message']}")

            # 중복 메시지에서 원본 메시지의 id를 가져옴.
            original_id = df.iloc[similar_items[0]]['original_message_id']
            # 만약 original_id가 Null 일 경우, 중복 메시지가 원본이다.
            if original_id is None:
                # original_id 를 중복 메시지의 id로 설정
                original_id = df.iloc[similar_items[0]]['id']
            max_duplicate_count = df[df['original_message_id'] == original_id]['duplicate_count'].max()
            new_duplicate_count = max_duplicate_count + 1

            # max_duplicate_count 가 없으면 nan 이 된다. 이 때 0 대입.
            if math.isnan(new_duplicate_count):
                new_duplicate_count = 0

            # DB에 추가
            db_insert(session, message_id, request.chat_id, request.client_message_id, request.room_id, request.sent_at,
                      request.user_id, request.message, current_time, new_duplicate_count, original_id)

            print(f"중복된 메시지입니다. (원본 메시지 ID: {original_id}, 중복 횟수: {new_duplicate_count})")

            return {
                "message_id": message_id,
                "message": request.message,
                "is_duplicate": True,
                "original_id": original_id,
                "distance": distances[0],
                "duplicate_count": new_duplicate_count
            }
        else:
            db_insert(session, message_id, request.chat_id, request.client_message_id, request.room_id, request.sent_at,
                      request.user_id, request.message, current_time, 0, None)
            print("중복되지 않은 새로운 메시지입니다.")

            return {
                "message_id": message_id,
                "message": request.message,
                "is_duplicate": False
            }
        