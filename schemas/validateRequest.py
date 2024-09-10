from pydantic import BaseModel

class ValidateRequest(BaseModel):
    chat_id: int
    client_message_id: int
    room_id: int
    user_id: int
    message: str
    sent_at: int
