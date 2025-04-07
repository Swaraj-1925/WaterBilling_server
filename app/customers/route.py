from datetime import date

import jwt
from fastapi import APIRouter, Depends, status, UploadFile
from fastapi.params import Query, Form, File
from sqlmodel import Session, select

from app.auth.authentication import hash_password, create_access_token, verify_password, get_token_data
from app.db.models import Customers, Bills
from app.db.session import get_session
from app.meter_readers.azure_blob_storage import upload_blob
from utils.logger import logger
from utils.response import APIResponse
from utils.response_schemas import CustomerSignup, Signin

customer_router = APIRouter(prefix="/customers", tags=["customers"])

@customer_router.post("/signup",description="Sing up route for customer")
async  def customer_signup(customer_data: CustomerSignup, db: Session = Depends(get_session)):
    """Handles customer signup and returns a JWT token"""
    try:

        query = select(Customers).where(Customers.phone == customer_data.phone)
        existing_customer = (await db.exec(query)).first()
        if existing_customer:
            logger.warning(f"Customer {existing_customer.id} already exists")
            return APIResponse.error(message="Customer already exists", status_code=status.HTTP_409_CONFLICT)

        hashed_password = hash_password(password=customer_data.password)
        new_customer = Customers(
            phone=customer_data.phone,
            email=customer_data.email,
            name=customer_data.name,
            hashed_password =hashed_password,
            address=customer_data.address,
        )
        db.add(new_customer)
        await db.commit()
        await db.refresh(new_customer)
        token = create_access_token({"phone": new_customer.phone, "email": new_customer.email})
        return APIResponse.success({"token": token}, status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Error in customer signup", exc_info=e)
        return APIResponse.error("Something went wrong with creating account of customer")

@customer_router.post("/login",description="Sing up route for customer")
async def customer_login(customer_data: Signin, db: Session = Depends(get_session)):
    """Handles customer signin and returns a JWT token"""
    try:

        query = select(Customers).where(Customers.phone == customer_data.phone)
        result = await db.exec(query)
        existing_customer = result.first()
        if not existing_customer:
            logger.warning("Customer signup failed")
            return APIResponse.error(message="Customer dont Exist", status_code=status.HTTP_404_NOT_FOUND)
        check_password = verify_password(plain_password=customer_data.password, hashed_password=existing_customer.hashed_password)
        if not check_password:
            logger.warning("Customer signin failed wrong password")
            return APIResponse.error("Customer signin failed wrong password",status_code=status.HTTP_404_NOT_FOUND)

        token = create_access_token({"phone": existing_customer.phone, "email": existing_customer.email})

        return APIResponse.success({"token": token},status_code=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error("Error in customer signup", exc_info=e)
        return APIResponse.error("Something went wrong with login of customer")

@customer_router.get("/get_bill",description="Get Bills")
async def get_bill(all_result:bool = Query(default=False, description="Return all response"), customer=Depends(get_token_data), db: Session = Depends(get_session)):
    try:
        query = select(Bills).where(Bills.phone == customer.phone).order_by(Bills.id.desc())
        result = await db.exec(query)

        bills = result.all() if all_result else result.first()
        if all_result:
            last_bill = db.exec(query).all()
        else:
            last_bill = db.exec(query).first()
        if not last_bill:
            return APIResponse.error(message="No bills found for this customer", status_code=status.HTTP_404_NOT_FOUND)
        return APIResponse.success(last_bill)
    except Exception as e:
        logger.error("Error while getting all the bills", exc_info=e)
        return APIResponse.error("Something went wrong with getting last bill")

