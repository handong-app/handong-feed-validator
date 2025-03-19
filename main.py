import subprocess
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError

from exceptions.base_exception import DatabaseException, APIException
from routers.validate_router import validate_router
from exceptions.handlers import global_exception_handler, db_exception_handler, api_exception_handler

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 서버 시작시 실행
#     task = asyncio.create_task(run_annoy_index_update())
#     yield
#     # 서버 종료시 실행
#     task.cancel()

app = FastAPI()
# lifespan 활성화 하려면, 아래 코드 주석해제.
# app = FastAPI(lifespan=lifespan)

# async def run_annoy_index_update():
#     while True:
#         subprocess.run(["python", "util/build_annoy_index_last_14days.py"], check=True)
#         print("Annoy index updated successfully")
#         await asyncio.sleep(86400)  # 24시간
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(DatabaseException, db_exception_handler)
app.add_exception_handler(SQLAlchemyError, db_exception_handler)


app.include_router(validate_router, prefix="/api/kafeed/validate")
