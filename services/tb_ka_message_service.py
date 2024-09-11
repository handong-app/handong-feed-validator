from models import TbKaMessage
from schemas.tb_ka_message_dto import TbKaMessageDto
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