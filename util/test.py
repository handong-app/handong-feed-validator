from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from annoy import AnnoyIndex
from datetime import datetime
import pandas as pd
import pickle
import math
import uuid

from util.database import engine


def db_insert(session, message_id, chat_id, client_message_id, room_id, sent_at, user_id, message, current_time, duplicate_count, original_id):
    try:
        session.execute(text(
            """
            INSERT INTO mydb_TbKaFeed 
            (id, chatId, clientMessageId, roomId, sentAt, userId, message, createdDate, modifiedDate, duplicate_count, original_message_id, deleted)
            VALUES (:id, :chatId, :clientMessageId, :roomId, :sentAt, :userId, :message, :createdDate, :modifiedDate, :duplicate_count, :original_message_id, :deleted)
            """
        ), {
            "id": message_id,
            "chatId": chat_id,
            "clientMessageId": client_message_id,
            "roomId": room_id,
            "sentAt": sent_at,
            "userId": user_id,
            "message": message,
            "createdDate": current_time,
            "modifiedDate": current_time,
            "duplicate_count": duplicate_count,
            "original_message_id": original_id,
            "deleted": "N"
        })
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"데이터 삽입 중 문제 발생: {e}")
    finally:
        print("데이터가 성공적으로 삽입되었습니다.")
        session.close()


def process_message():
    # TF-IDF 벡터화 모델 로드
    with open('./artifacts/tfidf_vectorizer.pkl', 'rb') as f:
        tfidf_vectorizer = pickle.load(f)

    # Annoy 인덱스 로드
    f = len(tfidf_vectorizer.get_feature_names_out())
    annoy_index = AnnoyIndex(f, 'angular')
    annoy_index.load('./artifacts/annoy_index.ann')

    # 기존 메시지 로드
    with engine.connect() as connection:
        df = pd.read_sql_table('mydb_TbKaFeed', con=connection)

    user_input = """[D-2]🫢하버드보다 들어가기 어렵다는 미네르바 대학의 교육이 한동에 들어온다고⁉️🫢"""
    user_vector = tfidf_vectorizer.transform([user_input]).toarray().flatten()

    n_similar = 1
    similar_items, distances = annoy_index.get_nns_by_vector(user_vector, n_similar, include_distances=True)

    threshold = 1.1
    chat_id = 12345678901234567
    client_message_id = 12345678901234567
    room_id = 12345678901234567
    sent_at = 1609459200
    user_id = 12345678901234567

    for idx in range(len(distances)):
        Session = sessionmaker(bind=engine)
        session = Session()

        message_id = str(uuid.uuid4()).replace('-', '')
        current_time = datetime.now()

        if distances[idx] < threshold:
            original_id = df.iloc[similar_items[idx]]['original_message_id']
            if original_id is None:
                original_id = df.iloc[similar_items[idx]]['id']
            max_duplicate_count = df[df['original_message_id'] == original_id]['duplicate_count'].max()
            new_duplicate_count = max_duplicate_count + 1

            if math.isnan(new_duplicate_count):
                new_duplicate_count = 0

            db_insert(session, message_id, chat_id, client_message_id, room_id, sent_at, user_id, user_input,
                      current_time, new_duplicate_count, original_id)
            print(f"중복된 메시지입니다. (원본 메시지 ID: {original_id}, 중복 횟수: {new_duplicate_count})")

        else:
            db_insert(session, message_id, chat_id, client_message_id, room_id, sent_at, user_id, user_input,
                      current_time, 0, None)
            print("중복되지 않은 새로운 메시지입니다.")


if __name__ == "__main__":
    process_message()