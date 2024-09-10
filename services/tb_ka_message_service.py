from models import TbKaMessage
from schemas.tb_ka_message_dto import TbKaMessageDto


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

            return new_message
        except Exception as e:
            # 문제가 발생하면 롤백
            session.rollback()
            print(f"데이터 삽입 중 문제 발생: {e}")
            raise
        finally:
            session.close()