from fastapi import FastAPI
from routers.validateRouter import validate_router


app = FastAPI()
app.include_router(validate_router, prefix="/api/kafeed")