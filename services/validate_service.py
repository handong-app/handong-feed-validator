import os
import pickle
import pandas as pd

from sqlalchemy.orm import Session
from annoy import AnnoyIndex

from services.tb_subject_service import TbSubjectService
from services.tb_ka_message_service import TbKaMessageService
from schemas.tb_ka_message_dto import TbKaMessageDto
from schemas.validate_dto import ValidateDto
from util.database import engine



class ValidateService:
    @staticmethod
    def process_validate(request: ValidateDto.ValidateReqDto, session: Session) -> ValidateDto.ValidateResDto:
        # case 1 : 기존 data 가 없는 경우 (artifacts 가 없는 경우)
        if not os.path.exists('artifacts/tfidf_vectorizer.pkl'):
            return ValidateService.first_message_routine(request, session)

        # 거리 계산 및 유사 message get
        distances_similar_items_dto = ValidateService.get_distances_and_similar_items(
            ValidateDto.GetDistanceServDto(
                message = request.message,
                n_similar = 1))
        distances, similar_items = distances_similar_items_dto.distances, distances_similar_items_dto.similar_items

        # 0에 가까울 수록 유사한 정도가 높다. 0은 완전히 같은 것이다.
        # 중복 아닌 것을 중복 처리 하는 것 보다, 중복인 것을 못잡는 상황이 더 낫다고 판단 -> 임계값 하향 조정.
        threshold = 1.08

        # 기존 메시지 로드
        with engine.connect() as connection:
            df = pd.read_sql_table('TbKaMessage', con=connection)

        # 가장 유사한 메세지의 정보
        similar_message_id = df.iloc[similar_items[0]]['id']
        similar_subject_id = df.iloc[similar_items[0]]['subject_id']

        # case 2 : message 의 거리가 임계값 이상인 경우
        if distances[0] > threshold:
            print("새로운 메세지")
            return ValidateService.first_message_routine(request, session)

        # case 3 - 1 : message 의 거리가 0인 경우
        elif distances[0] == 0:
            print("중복 메세지 - 일치")
            # 메시지가 완전히 일치하므로 기존 행의 last_sent_at 업데이트
            ValidateService.update_duplicated(session, request, similar_subject_id, similar_message_id)

            return ValidateDto.ValidateResDto(
                message_id=similar_message_id,
                is_duplicate=True,
                subject_id=similar_subject_id
            )

        # case 3 - 2 :  message 의 거리가 임계값 이하인 경우
        elif distances[0] <= threshold:
            print("중복 메세지")
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
            # ValidateService.db_insert(session, message_id, request.chat_id, request.client_message_id, request.room_id, request.sent_at,
            #           request.user_id, request.message, current_time, new_duplicate_count, original_id)

            print(f"중복된 메시지입니다. (원본 메시지 ID: {original_id}, 중복 횟수: {new_duplicate_count})")

        return ValidateDto.ValidateResDto(
                message_id=similar_message_id,
                is_duplicate=True,
                subject_id=similar_subject_id
            )

    @staticmethod
    def first_message_routine(request: ValidateDto.ValidateReqDto, session: Session) -> ValidateDto.ValidateResDto:
        subject_id = TbSubjectService.create_new_subject(session, request.sent_at, request.chat_id)

        save_req_dto = TbKaMessageDto.SaveReqDto(
            chat_id=request.chat_id,
            client_message_id=request.client_message_id,
            room_id=request.room_id,
            last_sent_at=request.sent_at,
            user_id=request.user_id,
            message=request.message,
            subject_id=subject_id,
        )

        tb_ka_message = TbKaMessageService.save_ka_message(session, save_req_dto)

        return ValidateDto.ValidateResDto(
            message_id=tb_ka_message.id,
            is_duplicate=False,
            subject_id=tb_ka_message.subject_id
        )

    @staticmethod
    def update_duplicated(session: Session, dto: ValidateDto.ValidateReqDto, subject_id: int, similar_message_id: str):
        TbKaMessageService.update_when_duplicated(session, dto, similar_message_id)
        TbSubjectService.update_last_sent_at(session, dto, subject_id)

    @staticmethod
    def get_distances_and_similar_items(dto: ValidateDto.GetDistanceServDto) -> ValidateDto.DistanceSimilarItemServDto:
        # TF-IDF 벡터화 모델 로드
        with open('artifacts/tfidf_vectorizer.pkl', 'rb') as f:
            tfidf_vectorizer = pickle.load(f)

        # Annoy 인덱스 로드
        f = len(tfidf_vectorizer.get_feature_names_out())
        annoy_index = AnnoyIndex(f, 'angular')
        annoy_index.load('artifacts/annoy_index.ann')

        # 입력된 텍스트 TF-IDF 벡터화
        request_message_vector = tfidf_vectorizer.transform([dto.message]).toarray().flatten()

        # 유사한 메시지 검색
        similar_items, distances = annoy_index.get_nns_by_vector(request_message_vector, dto.n_similar, include_distances=True)

        return ValidateDto.DistanceSimilarItemServDto(
            distances=distances,
            similar_items=similar_items
        )
