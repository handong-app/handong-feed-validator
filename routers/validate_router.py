from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.bulk_validate_dto import BulkValidateDto
from services.validate_service import ValidateService
from schemas.validate_dto import ValidateDto
from util.database import get_db


validate_router = APIRouter()


@validate_router.post("", response_model=ValidateDto.ValidateResDto)
async def process_single_validate(request: ValidateDto.ValidateReqDto, db: Session = Depends(get_db)):
    try:
        return ValidateService.process_single_validate(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@validate_router.post("/bulk", response_model=BulkValidateDto.BulkValidateResDto)
async def process_bulk_validate(bulk_request: BulkValidateDto.BulkValidateReqDto, db: Session = Depends(get_db)):
    try:
        result = await ValidateService.process_bulk_validate(bulk_request, db)
        return BulkValidateDto.BulkValidateResDto(requests=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
