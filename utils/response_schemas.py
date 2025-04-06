from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel


class CustomerSignup(BaseModel):
    phone: int
    email: Optional[str]
    name: str
    address: str
    password: str

class Signin(BaseModel):
    phone: int
    password: str

class MeterReaderSignup(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class CalculateBill(BaseModel):
    phone: int
    reading: int
    image_url: str
    modified: bool
