import os
import pickle
import pandas as pd

from sqlalchemy.orm import Session
from annoy import AnnoyIndex

from schemas.tb_ka_message_dto import TbKaMessageDto
from util.build_annoy_index import build_annoy_index
from services.tb_subject_service import TbSubjectService
from services.tb_ka_message_service import TbKaMessageService
from schemas.validate_dto import ValidateDto
from util.database import engine



class ValidateService:
    @staticmethod
    def process_validate(request: ValidateDto.ValidateReqDto, session: Session) -> ValidateDto.ValidateResDto:
        # 0에 가까울 수록 유사한 정도가 높다. 0은 완전히 같은 것이다.
        # 중복 아닌 것을 중복 처리 하는 것 보다, 중복인 것을 못잡는 상황이 더 낫다고 판단 -> 임계값 하향 조정.
        threshold = 0.8

        # case 1 : 기존 data 가 없는 경우 (artifacts 가 없는 경우)
        if not os.path.exists('artifacts/tfidf_vectorizer.pkl'):
            # Table 에 아예 data 가 없을 때
            if TbKaMessageService.is_empty(session):
                print("첫 메세지, new_message_routine 실행")
                return ValidateService.new_message_routine(
                    session, request,
                    TbKaMessageDto.AdditionalFieldServDto(
                        threshold = threshold,
                        distance = -1,
                        similar_id = "FIRST MESSAGE"))
            # Artifacts 만 없을 때
            else:
                print("Artifacts 없음, 생성후 routine 시작")
                build_annoy_index()

        # 거리 계산 및 유사 message get
        distances_similar_items_dto = ValidateService.get_distances_and_similar_items(
            ValidateDto.GetDistanceServDto(
                message = request.message,
                n_similar = 1))
        distances, similar_items = distances_similar_items_dto.distances, distances_similar_items_dto.similar_items

        # 기존 메시지 로드
        with engine.connect() as connection:
            df = pd.read_sql_table('TbKaMessage', con=connection)

        # 가장 유사한 메세지의 정보
        similar_id = df.iloc[similar_items[0]]['id']
        similar_subject_id = df.iloc[similar_items[0]]['subject_id']

        print("거리 측정 끝, 케이스 판별 시작")
        # case 2 : message 의 거리가 임계값 이상인 경우
        if distances[0] > threshold:
            print("case 2: 새로운 메세지")
            return ValidateService.new_message_routine(
                session, request,
                TbKaMessageDto.AdditionalFieldServDto(
                    threshold = threshold,
                    distance = distances[0],
                    similar_id = similar_id))

        elif distances[0] <= threshold:
            print("거리가 임계값 이하, case 3 판별 시작")
            # case 3 - 1 : message 의 거리가 0인 경우
            if distances[0] == 0.0:
                print("distances[0] == 0.0 이므로 중복 판별 시작")
                print("len(similar_items) : ",len(similar_items))
                for idx in range(len(similar_items)):
                    if distances[idx] != 0.0:
                        break
                    if request.message == df.iloc[similar_items[idx]]['message']:
                        print(f"중복 메세지 (거리: {distances[0]})")
                        return ValidateService.duplicate_message_routine(
                            session, request,
                            TbKaMessageDto.AdditionalFieldServDto(
                                subject_id = similar_subject_id,
                                threshold = threshold,
                                distance = df.iloc[similar_items[idx]]['distance'],
                                similar_id = similar_id))
                    idx += 1
                print("중복 아님")
            # case 3 - 2 :  message 의 거리가 임계값 이하인 경우
            print(f"유사 메세지 (거리: {distances[0]})")
            return ValidateService.similar_message_routine(
                session, request,
                TbKaMessageDto.AdditionalFieldServDto(
                    subject_id = similar_subject_id,
                    threshold = threshold,
                    distance = distances[0],
                    similar_id = similar_id))


    @staticmethod
    def new_message_routine(session: Session, validate_req_dto: ValidateDto.ValidateReqDto, additional_field_dto: TbKaMessageDto.AdditionalFieldServDto) -> ValidateDto.ValidateResDto:
        subject_id = TbSubjectService.create_new_subject(session, validate_req_dto.sent_at, validate_req_dto.chat_id)
        additional_field_dto.subject_id = subject_id
        save_req_dto = validate_req_dto.to_save_req_dto(additional_field_dto)
        tb_ka_message = TbKaMessageService.save_ka_message(session, save_req_dto)

        return ValidateDto.ValidateResDto(
            message_id = tb_ka_message.id,
            chat_id = tb_ka_message.chat_id,
            message = "New message",
            subject_id = tb_ka_message.subject_id,
        )

    @staticmethod
    def duplicate_message_routine(session: Session, validate_req_dto: ValidateDto.ValidateReqDto, additional_field_dto: TbKaMessageDto.AdditionalFieldServDto) -> ValidateDto.ValidateResDto:
        TbKaMessageService.update_when_duplicated(session, validate_req_dto, additional_field_dto)
        TbSubjectService.update_last_sent_info(session, validate_req_dto, additional_field_dto.subject_id)

        return ValidateDto.ValidateResDto(
            message_id = additional_field_dto.similar_id,
            chat_id = validate_req_dto.chat_id,
            message = "Duplicate message",
            subject_id = additional_field_dto.subject_id
        )

    @staticmethod
    def similar_message_routine(session: Session, validate_req_dto: ValidateDto.ValidateReqDto, additional_field_dto: TbKaMessageDto.AdditionalFieldServDto) -> ValidateDto.ValidateResDto:
        tb_ka_message = TbKaMessageService.save_ka_message(session, validate_req_dto.to_save_req_dto(additional_field_dto))
        TbSubjectService.update_last_sent_info(session, validate_req_dto, additional_field_dto.subject_id)

        return ValidateDto.ValidateResDto(
            message_id = tb_ka_message.id,
            chat_id = tb_ka_message.chat_id,
            message = f"Similar message, distance: {additional_field_dto.distance}",
            subject_id = tb_ka_message.subject_id
        )

    @staticmethod
    def get_distances_and_similar_items(get_distance_serv_dto: ValidateDto.GetDistanceServDto) -> ValidateDto.DistanceSimilarItemServDto:
        # TF-IDF 벡터화 모델 로드
        with open('artifacts/tfidf_vectorizer.pkl', 'rb') as f:
            tfidf_vectorizer = pickle.load(f)

        # Annoy 인덱스 로드
        f = len(tfidf_vectorizer.get_feature_names_out())
        annoy_index = AnnoyIndex(f, 'angular')
        annoy_index.load('artifacts/annoy_index.ann')

        # 입력된 텍스트 TF-IDF 벡터화
        request_message_vector = tfidf_vectorizer.transform([get_distance_serv_dto.message]).toarray().flatten()

        # 유사한 메시지 검색
        similar_items, distances = annoy_index.get_nns_by_vector(request_message_vector, get_distance_serv_dto.n_similar, include_distances=True)

        return ValidateDto.DistanceSimilarItemServDto(
            distances = distances,
            similar_items = similar_items
        )
