from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.validate_service import ValidateService
from schemas.validate_dto import ValidateDto
from util.database import get_db


validate_router = APIRouter()


@validate_router.post("/validate", response_model=ValidateDto.ValidateResDto)
async def process_validate(request: ValidateDto.ValidateReqDto, db: Session = Depends(get_db)):
    try:
        return ValidateService.process_validate(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

