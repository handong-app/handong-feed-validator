from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas.validate_request import ValidateRequest
from services.validate_service import ValidateService
from schemas.validate_response import ValidateResponse
from util.database import get_db


validate_router = APIRouter()


@validate_router.post("/validate", response_model=ValidateResponse)
async def process_feed(request:ValidateRequest, db: Session = Depends(get_db)):
    try:
        return ValidateService.process_validate(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
