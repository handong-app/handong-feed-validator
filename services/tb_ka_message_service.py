from sqlalchemy import text
from sqlalchemy.orm import Session

from models import TbKaMessage
from schemas.tb_ka_message_dto import TbKaMessageDto
from schemas.validate_dto import ValidateDto
from util.build_annoy_index import build_annoy_index


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
                subject_id=save_req_dto.subject_id
            )
            session.add(new_message)
            session.commit()

            # 새 Message 저장 후 index build
            build_annoy_index()

            return new_message
        except Exception as e:
            session.rollback()
            print(f"데이터 삽입 중 문제 발생: {e}")
            raise

    @staticmethod
    def update_when_duplicated(session: Session, dto: ValidateDto.ValidateReqDto, message_id: str):
        session.execute(text(
            """
            UPDATE TbKaMessage
            SET last_sent_at = :last_sent_at, chat_id = :chat_id, client_message_id = :client_message_id, room_id = :room_id, user_id = :user_id
            WHERE id = :message_id
            """
        ), {
            "message_id": message_id,
            "last_sent_at": dto.sent_at,
            "chat_id": dto.chat_id,
            "client_message_id": dto.client_message_id,
            "room_id": dto.room_id,
            "user_id": dto.user_id
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