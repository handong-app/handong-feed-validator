from pydantic import BaseModel
from typing import Optional


class TbKaMessageDto:
    class SaveReqDto(BaseModel):
        chat_id: int
        client_message_id: int
        room_id: int
        last_sent_at: int
        user_id: int
        message: str
        threshold: float
        distance: float
        similar_id: str
        subject_id: int

    class AdditionalFieldServDto(BaseModel):
        subject_id: Optional[int] = None
        threshold: float
        distance: float
        similar_id: str