from sqlalchemy import text
from sqlalchemy.orm import Session

from config.constants import DatabaseConfig
from models import TbKaMessage
from schemas.tb_ka_message_dto import TbKaMessageDto
from schemas.validate_dto import ValidateDto
from util.date_tool import get_seoul_time


class TbKaMessageService:
    @staticmethod
    def save_ka_message(session, save_req_dto: TbKaMessageDto.SaveReqDto) -> TbKaMessage:
        try:
            new_message = TbKaMessage(
                chat_id=save_req_dto.chat_id,
                client_message_id=save_req_dto.client_message_id,
                room_id=save_req_dto.room_id,
                last_sent_at=save_req_dto.last_sent_at,
                user_id=save_req_dto.user_id,
                message=save_req_dto.message,
                threshold=save_req_dto.threshold,
                distance=save_req_dto.distance,
                similar_id=save_req_dto.similar_id,
                subject_id=save_req_dto.subject_id
            )
            session.add(new_message)
            session.commit()

            return new_message
        except Exception as e:
            session.rollback()
            print(f"데이터 삽입 중 문제 발생: {e}")
            raise

    @staticmethod
    def update_when_duplicated(session: Session, dto: ValidateDto.ValidateReqDto,  additional_field_dto: TbKaMessageDto.AdditionalFieldServDto):
        session.execute(text(
            # 중복메세지는 similar_id 값을 변경하지 않음.
            # message 값이 정확히 일치하므로 변경하면 안된다.
            """
            UPDATE TbKaMessage
            SET chat_id = :chat_id, client_message_id = :client_message_id, room_id = :room_id, user_id = :user_id, 
                threshold = :threshold, distance = :distance, last_sent_at = :last_sent_at, updated_at = :updated_at
            WHERE id = :similar_id
            """
        ), {
            "chat_id": dto.chat_id,
            "client_message_id": dto.client_message_id,
            "room_id": dto.room_id,
            "user_id": dto.user_id,
            "similar_id": additional_field_dto.similar_id,
            "threshold": additional_field_dto.threshold,
            "distance": additional_field_dto.distance,
            "last_sent_at": dto.sent_at,
            "updated_at": get_seoul_time()
        })
        session.commit()

    @staticmethod
    def is_empty(session: Session):
        try:
            count = session.query(TbKaMessage).count()
            if count == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"오류 발생: {e}")

    @staticmethod
    def is_empty_last_14days(session: Session):
        try:
            result = session.execute(text(DatabaseConfig.GET_TbKaMessage_LAST_14DAYS))
            count = result.scalar()  # 쿼리 결과에서 첫 번째 값을 가져옴

            if count == 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"오류 발생: {e}")
            return False  # 오류 발생 시 False 를 기본 값으로 반환