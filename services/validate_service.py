import math
import os
import uuid
import pickle
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session
from annoy import AnnoyIndex
import pandas as pd

from tb_subject_service import TbSubjectService
from util.database import engine
from schemas.validateRequest import ValidateRequest

class ValidateService:
    @staticmethod
    def process_validate(request: ValidateRequest, session: Session):
        # 기존 data 가 하나도 없을 시
        if not os.path.exists('artifacts/tfidf_vectorizer.pkl'):
            subject_id = TbSubjectService.create_new_subject(session, request.sent_at, request.chat_id)
            ValidateService.db_insert(session, request, subject_id)
            return {
                "message_id": str(uuid.uuid4()).replace('-', ''),
                "message": request.message,
                "is_duplicate": False
            }

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


        print(request.message)
        print()
        # 입력된 텍스트 TF-IDF 벡터화
        request_message_vector = tfidf_vectorizer.transform([request.message]).toarray().flatten()

        # 가장 유사한 메시지 검색
        n_similar = 1
        similar_items, distances = annoy_index.get_nns_by_vector(request_message_vector, n_similar, include_distances=True)

        # 0에 가까울 수록 유사한 정도가 높다. 0은 완전히 같은 것이다.
        # 중복 아닌 것을 중복 처리 하는 것 보다, 중복인 것을 못잡는 상황이 더 낫다고 판단, 임계값 하향 조정.
        threshold = 1.08

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
            print("original_id:",original_id)
            # 만약 original_id가 Null 일 경우, 중복 메시지가 원본이다.
            # original_id 설정해주고, 중복 횟수 1로 설정.
            if original_id is None:
                # original_id 를 중복 메시지의 id로 설정
                original_id = df.iloc[similar_items[0]]['id']
                print("유사메시지가 원본:",original_id)
                new_duplicate_count = 1
                print("new_duplicate_count:", new_duplicate_count)
            else:
                max_duplicate_count = df[df['original_message_id'] == original_id]['duplicate_count'].max()
                print("max_duplicate_count:",max_duplicate_count)
                new_duplicate_count = max_duplicate_count + 1
                print("new_duplicate_count:",new_duplicate_count)


            # DB에 추가
            ValidateService.db_insert(session, message_id, request.chat_id, request.client_message_id, request.room_id, request.sent_at,
                      request.user_id, request.message, current_time, new_duplicate_count, original_id)

            print(f"중복된 메시지입니다. (원본 메시지 ID: {original_id}, 중복 횟수: {new_duplicate_count})")

            res = {
                "message_id": message_id,
                "message": request.message,
                "is_duplicate": True,
                "original_id": original_id,
                "distance": distances[0],
                "duplicate_count": new_duplicate_count
            }
        else:
            ValidateService.db_insert(session, message_id, request.chat_id, request.client_message_id, request.room_id, request.sent_at,
                      request.user_id, request.message, current_time, 0, None)
            print("중복되지 않은 새로운 메시지입니다.")

            res =  {
                "message_id": message_id,
                "message": request.message,
                "is_duplicate": False
            }

        return res

