from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.validateRequest import ValidateRequest
from services.validateService import ValidateService
from schemas.validateResponse import ValidateResponse
from util.database import get_db


validate_router = APIRouter()


@validate_router.post("/validate", response_model=ValidateResponse)
async def process_feed(request:ValidateRequest, db: Session = Depends(get_db)):
    try:
        return ValidateService.process_validate(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
