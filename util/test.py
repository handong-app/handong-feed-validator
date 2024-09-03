from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from annoy import AnnoyIndex
from datetime import datetime
import pandas as pd
import pickle
import math
import uuid

from util.database import engine, db_insert


# TF-IDF 벡터화 모델 로드
with open('tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)


# Annoy 인덱스 로드
f = len(tfidf_vectorizer.get_feature_names_out())
annoy_index = AnnoyIndex(f, 'angular')
annoy_index.load('annoy_index.ann')

# 기존 메시지 로드
with engine.connect() as connection:
    df = pd.read_sql_table('mydb_TbKaFeed', con=connection)


# user_input = input("테스트 할 text 입력\n============================================\n\n")
# print("\n\n============================================\n\n")
user_input ="""[D-2]🫢하버드보다 들어가기 어렵다는 미네르바 대학의 교육이 한동에 들어온다고⁉️🫢

테스트테스으으으ㅡ으으ㅡ으으ㅡㅇ트ㅡ미네르바 대학의 혁신적인 교육 방식과 우수성을 경험할 수 있는 특별한 기회를 소개합니다람쥐

캠퍼스 없는 대학, 온라인 대학, 스타트업 대학, 하버드대학보다 들어가기 어려운 대학 등 미네르바 교육의 수식어만 보더라도 알 수 있듯이 미네르바 교육은 기존의 전통적인 교육 시스템과는 차별화된 혁신적인 접근 방식을 통해 학생들에게 글로벌 리더로 성장할 수 있는 기회를 제공하는 미래형 교육입니다. 

🗣️ 주요내용
- 미네르바-HGU 4C 교과목 소개 및 수업방식 안내
- 질의응답

⏰ 일시
- 영어 버전 설명회 : 2024.07.15(월) 10:30am

💻 장소
- 온라인(Zoom)

🗳️신청방법
- 구글폼 작성(설명회 전일 자정까지)
   https://forms.gle/rUtubj5zpyth89W97
   🔗신청자 한해 당일 문자로 줌 링크 발송

한동대학교에서는 전공을 초월하여 창의적, 비판적으로 사고하고 공동체 안에서 효과적으로 소통, 협력할 수 있는 
역량을 함양할 수 있도록, 미네르바 대학의 4C (Critical Thinking, Communication, Collaboration, Creativity) 교과목을 도입하고 2024학년도 2학기부터 운영을 시작합니다.

교과목과 수업 방식에 대한 이해를 위해 학생 대상 설명회를 개최하오니, 학생 여러분의 많은 참여 바랍니다.🙌"""

# 입력된 텍스트 TF-IDF 벡터화
user_vector = tfidf_vectorizer.transform([user_input]).toarray().flatten()

# 가장 유사한 메시지 검색
n_similar = 1
similar_items, distances = annoy_index.get_nns_by_vector(user_vector, n_similar, include_distances=True)

threshold = 1.1

# 요청으로부터 받은 데이터를 가정
chat_id = 12345678901234567
client_message_id = 12345678901234567
room_id = 12345678901234567
sent_at = 1609459200
user_id = 12345678901234567

for idx in range(len(distances)):
    # 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()

    # 메시지 ID 생성 (UUID)
    message_id = str(uuid.uuid4()).replace('-', '')
    print(message_id)
    # 현재 시간으로 createdDate와 modifiedDate 설정
    current_time = datetime.now()
    print(current_time)

    if distances[idx] < threshold:
        print("유사한 항목 인덱스:", similar_items[idx])
        print(f"중복된 메시지입니다. (거리: {distances[idx]})")
        print(f"유사한 메시지\n\n {df.iloc[similar_items[idx]]['message']}")


        # 중복 메시지에서 원본 메시지의 id를 가져옴.
        original_id = df.iloc[similar_items[idx]]['original_message_id']
        # 만약 original_id가 Null 일 경우, 중복 메시지가 원본이다.
        if original_id is None:
            # original_id 를 중복 메시지의 id로 설정
            original_id = df.iloc[similar_items[idx]]['id']
        max_duplicate_count = df[df['original_message_id'] == original_id]['duplicate_count'].max()
        new_duplicate_count = max_duplicate_count + 1

        if math.isnan(new_duplicate_count):
            new_duplicate_count = 0

        # DB에 추가
        try:
            db_insert(session, message_id, chat_id, client_message_id, room_id, sent_at, user_id, user_input, current_time,new_duplicate_count,original_id)
        except Exception as e:
            session.rollback()
            print(f"데이터 삽입 중 문제 발생: {e}")
        finally:
            print("데이터가 성공적으로 삽입되었습니다.")
            session.close()

        print(f"중복된 메시지입니다. (원본 메시지 ID: {original_id}, 중복 횟수: {new_duplicate_count})")

    else:
        # DB에 추가
        try:
            db_insert(session, message_id, chat_id, client_message_id, room_id, sent_at, user_id, user_input,
                      current_time, 0, None)
        except Exception as e:
            session.rollback()
            print(f"데이터 삽입 중 문제 발생: {e}")
        finally:
            print("데이터가 성공적으로 삽입되었습니다.")
            session.close()
        print("중복되지 않은 새로운 메시지입니다.")

