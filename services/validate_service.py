import asyncio
from sqlalchemy.orm import Session
from typing import List
from schemas.bulk_validate_dto import BulkValidateDto
from schemas.tb_ka_message_dto import TbKaMessageDto
from services.tb_subject_service import TbSubjectService
from services.tb_ka_message_service import TbKaMessageService
from services.index_manager import IndexManager
from schemas.validate_dto import ValidateDto
from util.database import SessionLocal
from util.io_utils import output_ln
from util.log_utils import save_log


class ValidateService:
    @staticmethod
    async def process_bulk_validate(bulk_request: BulkValidateDto.BulkValidateReqDto, db: Session) -> List[ValidateDto.ValidateResDto]:
        IndexManager.ensure_index()

        # 2. 비동기로 요청 처리
        tasks = [
            asyncio.to_thread(ValidateService.validate, req, db)
            for req in bulk_request.requests
        ]
        results = await asyncio.gather(*tasks)
        return results

    @staticmethod
    def process_single_validate(request: ValidateDto.ValidateReqDto, db: Session) -> ValidateDto.ValidateResDto:
        # 1. 인덱스 상태 확인 및 빌드 (최신 상태 보장)
        IndexManager.ensure_index()

        # 2. 요청 처리
        return ValidateService.validate(request, db)

    @staticmethod
    def validate(request: ValidateDto.ValidateReqDto, session: Session) -> ValidateDto.ValidateResDto:
        # validate 내부에서 독립적인 DB 세션 생성
        with SessionLocal() as local_session:
            return ValidateService._perform_validation(request, local_session)

    @staticmethod
    def _perform_validation(request: ValidateDto.ValidateReqDto, session: Session) -> ValidateDto.ValidateResDto:
        """주어진 요청 메시지에 대해 Annoy 인덱스를 사용해 유사 메시지 검색 및 처리로직 수행."""

        # 임계값 설정 (유사도 기준)
        # 0에 가까울 수록 유사한 정도가 높다.
        # 중복 아닌 것을 중복 처리 하는 것 보다, 중복인 것을 못잡는 상황이 더 낫다고 판단 -> 임계값 하향 조정.
        threshold = 0.8

        # 1. Annoy 인덱스, TF-IDF vectorizer, 14일치 데이터 로드
        vectorizer = IndexManager.load_tfidf_vectorizer()
        annoy_index = IndexManager.load_annoy_index(vectorizer)
        df_14days = IndexManager.load_last_14days_dataframe()
        latest_artifact_time = IndexManager.get_latest_artifact_time()
        latest_data_update_time = IndexManager.get_latest_data_update_time()

        # 2. 메시지를 TF-IDF 벡터화
        request_vector = vectorizer.transform([request.message]).toarray().flatten()
        similar_items, distances = annoy_index.get_nns_by_vector(request_vector, n=1, include_distances=True)

        save_log(
            chat_id = request.chat_id,
            log_type = "INFO",
            message = "유사도 검색 실행 완료",
            latest_artifact_time = latest_artifact_time,
            latest_data_update_time = latest_data_update_time,
            distance = distances[0] if similar_items else None,
            status = "CHECKED",
            case_type= "UNDETERMINED",
            ip_address = request.ip_address,
            user_id = request.user_id
        )
        
        # 4. 유사 메시지가 없으면 새로운 메시지로 처리
        if not similar_items or distances[0] > threshold:
            output_ln("case 2: 새로운 메세지\n")
            save_log(
                chat_id=request.chat_id,
                log_type="INFO",
                message="새로운 메시지로 처리됨",
                latest_artifact_time=latest_artifact_time,
                latest_data_update_time=latest_data_update_time,
                status="WILL_BE_SAVED",
                distance=distances[0],
                case_type="NEW_MESSAGE",
                similar_message_id="NEW_MESSAGE",
                subject_id="UNDETERMINED",
                ip_address=request.ip_address,
                user_id=request.user_id
            )

            return ValidateService.new_message_routine(session, request, TbKaMessageDto.AdditionalFieldServDto(
                threshold=threshold,
                distance=distances[0] if similar_items else -1,
                similar_id="NEW_MESSAGE"
            ))

        # 5. 유사 메시지가 있으면 추가 정보 로드
        similar_id = df_14days.iloc[similar_items[0]]['id']
        similar_subject_id = df_14days.iloc[similar_items[0]]['subject_id']

        output_ln("거리 측정 끝, 케이스 판별 시작")

        if distances[0] <= threshold:
            output_ln("거리가 임계값 이하, case 3 판별 시작")

            # 3-1: 거리가 0인 경우, 완전히 동일한 메시지로 판단
            if distances[0] == 0.0:
                output_ln("distances[0] == 0.0 이므로 중복 판별 시작")
                for idx in range(len(similar_items)):
                    if distances[idx] != 0.0:
                        break
                    if request.message == df_14days.iloc[similar_items[idx]]['message']:
                        output_ln(f"중복 메세지 (거리: {distances[idx]}, 중복 메세지는 거리 -2로 저장)")
                        save_log(
                            chat_id=request.chat_id,
                            log_type="INFO",
                            message="중복 메시지 처리됨",
                            latest_artifact_time=latest_artifact_time,
                            latest_data_update_time=latest_data_update_time,
                            status="WILL_NOT_BE_SAVED",
                            distance=distances[idx],
                            case_type="DUPLICATE_MESSAGE",
                            similar_message_id=similar_id,
                            subject_id=similar_subject_id,
                            ip_address=request.ip_address,
                            user_id=request.user_id
                        )

                        return ValidateService.duplicate_message_routine(session, request, TbKaMessageDto.AdditionalFieldServDto(
                            subject_id = similar_subject_id,
                            threshold = threshold,
                            distance = -2,
                            similar_id = similar_id
                        ))

                output_ln("중복 아님")

            # 3-2: 거리가 임계값 이하인 경우, 유사 메시지로 처리
            output_ln(f"유사 메세지 (거리: {distances[0]})")

            save_log(
                chat_id=request.chat_id,
                log_type="INFO",
                message="유사 메시지로 처리됨",
                latest_artifact_time=latest_artifact_time,
                latest_data_update_time=latest_data_update_time,
                status="WILL_BE_SAVED",
                distance=distances[0],
                case_type="SIMILAR_MESSAGE",
                similar_message_id=similar_id,
                subject_id=similar_subject_id,
                ip_address=request.ip_address,
                user_id=request.user_id
            )

            return ValidateService.similar_message_routine(session, request, TbKaMessageDto.AdditionalFieldServDto(
                subject_id = similar_subject_id,
                threshold = threshold,
                distance = distances[0],
                similar_id = similar_id
            ))

        # 기본적으로 새로운 메시지로 처리
        return ValidateService.new_message_routine(
            session,
            request,
            TbKaMessageDto.AdditionalFieldServDto(
                threshold = threshold,
                distance = -1,
                similar_id = "NEW_MESSAGE"
            )
        )


    @staticmethod
    def new_message_routine(session: Session, validate_req_dto: ValidateDto.ValidateReqDto, additional_field_dto: TbKaMessageDto.AdditionalFieldServDto) -> ValidateDto.ValidateResDto:
        subject_id = TbSubjectService.create_new_subject(session, validate_req_dto.sent_at, validate_req_dto.chat_id)
        additional_field_dto.subject_id = subject_id
        save_req_dto = validate_req_dto.to_save_req_dto(additional_field_dto)
        tb_ka_message = TbKaMessageService.save_ka_message(session, save_req_dto)

        save_log(
            chat_id=validate_req_dto.chat_id,
            log_type="INFO",
            message="새로운 메시지 저장됨",
            status="SAVED",
            case_type="NEW_MESSAGE",
            subject_id=str(tb_ka_message.subject_id),
            similar_message_id=additional_field_dto.similar_id,
            ip_address=validate_req_dto.ip_address,
            user_id=validate_req_dto.user_id
        )

        return ValidateDto.ValidateResDto(
            message_id = tb_ka_message.id,
            chat_id = tb_ka_message.chat_id,
            message = "New message",
            subject_id = tb_ka_message.subject_id,
        )

    @staticmethod
    def duplicate_message_routine(session: Session, validate_req_dto: ValidateDto.ValidateReqDto, additional_field_dto: TbKaMessageDto.AdditionalFieldServDto) -> ValidateDto.ValidateResDto:
        # TbKaMessageService.update_when_duplicated(session, validate_req_dto, additional_field_dto)
        tb_ka_message = TbKaMessageService.save_ka_message(session, validate_req_dto.to_save_req_dto(additional_field_dto))
        TbSubjectService.update_last_sent_info(session, validate_req_dto, additional_field_dto.subject_id)

        save_log(
            chat_id=validate_req_dto.chat_id,
            log_type="INFO",
            message="중복 메시지 저장되지 않음.",
            status="NOT_SAVED",
            case_type="DUPLICATE_MESSAGE",
            subject_id=str(tb_ka_message.subject_id),
            similar_message_id=additional_field_dto.similar_id,
            ip_address=validate_req_dto.ip_address,
            user_id=validate_req_dto.user_id
        )

        return ValidateDto.ValidateResDto(
            message_id = tb_ka_message.id,
            chat_id = validate_req_dto.chat_id,
            message = "Duplicate message",
            subject_id = additional_field_dto.subject_id
        )

    @staticmethod
    def similar_message_routine(session: Session, validate_req_dto: ValidateDto.ValidateReqDto, additional_field_dto: TbKaMessageDto.AdditionalFieldServDto) -> ValidateDto.ValidateResDto:
        tb_ka_message = TbKaMessageService.save_ka_message(session, validate_req_dto.to_save_req_dto(additional_field_dto))
        TbSubjectService.update_last_sent_info(session, validate_req_dto, additional_field_dto.subject_id)

        save_log(
            chat_id=validate_req_dto.chat_id,
            log_type="INFO",
            message="유사 메시지 저장됨",
            status="SAVED",
            case_type="SIMILAR_MESSAGE",
            subject_id=str(tb_ka_message.subject_id),
            similar_message_id=additional_field_dto.similar_id,
            ip_address=validate_req_dto.ip_address,
            user_id=validate_req_dto.user_id
        )

        return ValidateDto.ValidateResDto(
            message_id = tb_ka_message.id,
            chat_id = tb_ka_message.chat_id,
            message = f"Similar message, distance: {additional_field_dto.distance}",
            subject_id = tb_ka_message.subject_id
        )

    # @staticmethod
    # def get_distances_and_similar_items(get_distance_serv_dto: ValidateDto.GetDistanceServDto) -> ValidateDto.DistanceSimilarItemServDto:
    #     # TF-IDF 벡터화 모델 로드
    #     with open(LocalPath.TFIDF_VECTORIZER_LAST_14DAYS, 'rb') as f:
    #         tfidf_vectorizer = pickle.load(f)
    #
    #     # Annoy 인덱스 로드
    #     f = len(tfidf_vectorizer.get_feature_names_out())
    #     annoy_index = AnnoyIndex(f, 'angular')
    #     annoy_index.load(LocalPath.ANNOY_INDEX_LAST_14DAYS)
    #
    #     # 입력된 텍스트 TF-IDF 벡터화
    #     request_message_vector = tfidf_vectorizer.transform([get_distance_serv_dto.message]).toarray().flatten()
    #
    #     # 유사한 메시지 검색
    #     similar_items, distances = annoy_index.get_nns_by_vector(request_message_vector, get_distance_serv_dto.n_similar, include_distances=True)
    #
    #     return ValidateDto.DistanceSimilarItemServDto(
    #         distances = distances,
    #         similar_items = similar_items
    #     )
    #