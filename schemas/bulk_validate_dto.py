from pydantic import BaseModel
from typing import List

from schemas.validate_dto import ValidateDto

class BulkValidateDto:
    class BulkValidateReqDto(BaseModel):
        requests: List[ValidateDto.ValidateReqDto]

    class BulkValidateResDto(BaseModel):
        requests: List[ValidateDto.ValidateResDto]
