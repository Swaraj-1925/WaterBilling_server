import os
from contextlib import asynccontextmanager

import uvicorn
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)