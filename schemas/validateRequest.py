from pydantic import BaseModel

class ValidateRequest(BaseModel):
    chat_id: int
    client_message_id: int
    room_id: int
    sent_at: int
    user_id: int
    message: str
