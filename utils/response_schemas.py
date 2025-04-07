from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel


class CustomerSignup(BaseModel):
    phone: str
    email: Optional[str]
    name: str
    address: str
    password: str

class Signin(BaseModel):
    phone: str
    password: str

class MeterReaderSignup(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    address: str

class CalculateBill(BaseModel):
    phone: str
    reading: int
    image_url: str
    modified: bool
