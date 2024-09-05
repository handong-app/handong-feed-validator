from fastapi import FastAPI
from contextlib import asynccontextmanager
import subprocess
import time
import asyncio

from routers.validateRouter import validate_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작시 실행
    task = asyncio.create_task(run_annoy_index_update())
    yield
    # 서버 종료시 실행
    task.cancel()

app = FastAPI()
# lifespan 활성화 하려면, 아래 코드 주석해제.
# app = FastAPI(lifespan=lifespan)

async def run_annoy_index_update():
    while True:
        subprocess.run(["python", "util/build_annoy_index.py"], check=True)
        print("Annoy index updated successfully")
        await asyncio.sleep(86400)  # 24시간

app.include_router(validate_router, prefix="/api/kafeed")