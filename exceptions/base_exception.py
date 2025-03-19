from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


class CustomBaseException(HTTPException):
    """ 기본적으로 FastAPI의 HTTPException을 확장한 커스텀 예외 """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class APIException(CustomBaseException):
    """ API 수준에서 발생한 예외를 포괄적으로 묶은 예외 """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ValidationException(CustomBaseException):
    """ 입력값 검증 오류 """
    def __init__(self, detail: str = "Validation exception"):
        super().__init__(status_code=422, detail=detail)

class DatabaseException(CustomBaseException):
    """ DB 관련 오류 """
    def __init__(self, detail: str = "Database exception"):
        super().__init__(status_code=500, detail=detail)