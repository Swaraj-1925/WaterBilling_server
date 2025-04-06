from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Customers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: int = Field(max_digits=10,nullable=False,unique=True)
    email: str
    name: str
    address: str
    hashed_password: str

    bills: List["Bills"] = Relationship(back_populates="customer")


class MeterReader(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: int = Field(max_digits=10,nullable=False,unique=True)
    hashed_password: str

    readings: List["Bills"] = Relationship(back_populates="reader")


class Bills(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: int = Field(foreign_key="customers.phone")
    reader_id: int = Field(foreign_key="meterreader.id")
    image_url: str

    reading_value: float
    reading_date: str
    due_date: str
    price: float
    modified:bool #the bill was modified after extracted data from the image

    customer: Customers = Relationship(back_populates="bills")
    reader: Optional[MeterReader] = Relationship(back_populates="readings")