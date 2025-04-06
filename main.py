from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.db.session import create_db_and_tables
from utils.logger import logger
from app.meter_readers.route import meter_reader_router
from app.customers.route import customer_router

@asynccontextmanager
async def init_db():
    await create_db_and_tables()
    yield
    logger.info("Shutting down db")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/",description="Initial routes")
def read_root():
    return {"message": "Wellcome Water meter billing server"}

app.include_router(meter_reader_router)
app.include_router(customer_router)