import asyncio

from fastapi import Request
from fastapi.responses import JSONResponse

from constants.enum import LogType, Status
from util.log_utils import save_log

async def global_exception_handler(request: Request, exc: Exception):
    """ 전역 예외 핸들러 (예상치 못한 오류) """
    error_message = f"Unhandled Exception: {str(exc)}"

    save_log(
        chat_id=-1,
        log_type=LogType.ERROR.value,
        message=error_message,
        status=Status.ERROR.value,
        ip_address=request.client.host if request.client else "UNKNOWN",
        user_id=None
    )

    return JSONResponse(
        status_code=500,
        content={"detail": error_message}
    )

async def api_exception_handler(request: Request, exc: Exception, status_code: int = 500):
    """ API 예외 핸들러 """
    error_message = f"API Exception: {str(exc)}"

    save_log(
        chat_id=-1,
        log_type=LogType.ERROR.value,
        message=error_message,
        status=Status.ERROR.value,
        ip_address=request.client.host if request.client else "UNKNOWN",
        user_id=None
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": error_message}
    )


async def db_exception_handler(request: Request, exc: Exception):
    """ 데이터베이스 예외 핸들러 """

    save_log(
        chat_id=-1,
        log_type=LogType.ERROR.value,
        message=f"Database Exception: {str(exc)}",
        status=Status.ERROR.value,
        ip_address=request.client.host if request.client else "UNKNOWN",
        user_id=None
    )

    return JSONResponse(
        status_code=500,
        content={"detail": f"데이터베이스 오류가 발생했습니다. 관리자에게 문의하세요. 내용: {str(exc)}"}
    )

