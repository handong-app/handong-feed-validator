from pydantic import BaseModel

class ValidateDto:
    class ValidateReqDto(BaseModel):
        chat_id: int
        client_message_id: int
        room_id: int
        user_id: int
        message: str
        sent_at: int

    class ValidateResDto(BaseModel):
        message_id: str
        is_duplicate: bool
        subject_id: int