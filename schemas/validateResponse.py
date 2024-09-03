from pydantic import BaseModel
from typing import Optional

class ValidateResponse(BaseModel):
    message_id: str
    message: str
    is_duplicate: bool
    original_id: Optional[str]
    distance: Optional[float]
