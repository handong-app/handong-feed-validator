from pydantic import BaseModel


class TbKaMessageDto:
    class SaveReqDto(BaseModel):
        chat_id: int
        client_message_id: int
        room_id: int
        last_sent_at: int
        user_id: int
        message: str
        subject_id: int