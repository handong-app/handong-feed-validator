from pydantic import BaseModel
from typing import Optional

class ValidateResponse(BaseModel):
    message_id: str
    is_duplicate: bool
    subject_id: int

