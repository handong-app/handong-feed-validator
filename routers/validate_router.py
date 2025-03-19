from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from exceptions.base_exception import APIException, DatabaseException
from schemas.bulk_validate_dto import BulkValidateDto
from services.validate_service import ValidateService
from schemas.validate_dto import ValidateDto
from util.database import get_db


validate_router = APIRouter()


@validate_router.post("", response_model=ValidateDto.ValidateResDto)
async def process_single_validate(request: Request, validate_req: ValidateDto.ValidateReqDto, db: Session = Depends(get_db)):
    try:
        client_ip = request.client.host
        validate_req.ip_address = client_ip
        return ValidateService.process_single_validate(validate_req, db)
    except DatabaseException as e:
        raise e
    except Exception as e:
        raise APIException(status_code=500, detail=str(e))

@validate_router.post("/bulk", response_model=BulkValidateDto.BulkValidateResDto)
async def process_bulk_validate(request: Request, bulk_validate_req: BulkValidateDto.BulkValidateReqDto, db: Session = Depends(get_db)):
    try:
        client_ip = request.client.host
        for req in bulk_validate_req.requests:
            req.ip_address = client_ip

        result = await ValidateService.process_bulk_validate(bulk_validate_req, db)
        return BulkValidateDto.BulkValidateResDto(requests=result)
    except DatabaseException as e:
        raise e
    except Exception as e:
        raise APIException(status_code=500, detail=str(e))
