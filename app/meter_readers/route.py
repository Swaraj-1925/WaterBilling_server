from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from sqlmodel import Session,select

from app.auth.authentication import hash_password, create_access_token, verify_password, get_token_data
from app.db.models import MeterReader, Customers, Bills
from app.db.session import get_session
from app.meter_readers.azure_blob_storage import upload_blob
from app.meter_readers.azure_meter_ocr import meter_ocr
from utils.logger import logger
from utils.response import APIResponse
from utils.response_schemas import MeterReaderSignup, Signin, CalculateBill

meter_reader_router = APIRouter(prefix="/meter", tags=["meter"])

@meter_reader_router.post("/signup",description="Sing up route for customer")
async  def meter_reader_signup(meter_reader_data: MeterReaderSignup, db: Session = Depends(get_session)):
    """Handles  meter reader signup and returns a JWT token"""
    try:

        query = select(MeterReader).where(MeterReader.phone == meter_reader_data.phone)
        result = await db.exec(query)
        existing = result.first()
        if existing:
            logger.warning(f"Customer {existing.id} already exists")
            return APIResponse.error(message="Customer already exists", status_code=status.HTTP_409_CONFLICT)

        hashed_password = hash_password(password=meter_reader_data.password)
        new_customer = MeterReader(
            phone=meter_reader_data.phone,
            email=meter_reader_data.email,
            name=meter_reader_data.name,
            hashed_password =hashed_password,
            address=meter_reader_data.address,
        )
        db.add(new_customer)
        await db.commit()
        await db.refresh(new_customer)
        token = create_access_token({"phone": new_customer.phone, "email": new_customer.email})
        return APIResponse.success({"token": token}, status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Error in customer signup", exc_info=e)
        return APIResponse.error("Something went wrong with creating account of customer")

@meter_reader_router.post("/login",description="Sing up route for customer")
async def meter_reader_login(meter_reader_data: Signin, db: Session = Depends(get_session)):
    """Handles meter reader login and returns a JWT token"""
    try:

        query = select(MeterReader).where(MeterReader.phone == meter_reader_data.phone)
        result = await db.exec(query)
        existing = result.first()
        if not existing:
            logger.warning("Customer signup failed")
            return APIResponse.error(message="Customer dont Exist", status_code=status.HTTP_404_NOT_FOUND)
        check_password = verify_password(plain_password=meter_reader_data.password, hashed_password=existing.hashed_password)
        if not check_password:
            logger.warning("Customer signin failed wrong password")
            return APIResponse.error("Customer signin failed wrong password",status_code=status.HTTP_404_NOT_FOUND)

        token = create_access_token({"phone": existing.phone, "email": existing.email})

        return APIResponse.success({"token": token},status_code=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error("Error in customer signup", exc_info=e)
        return APIResponse.error("Something went wrong with login of customer")

@meter_reader_router.post("/take_meter_reading",description="Upload an image and it will mark the reading accordingly")
async def take_meter_reading(
        phone: str = Form(...),
        meter_reader=Depends(get_token_data),
        image: UploadFile = File(..., description="Image of the meter reading"),
        db: Session = Depends(get_session)
):
    try:
        query = select(MeterReader).where(MeterReader.phone == meter_reader.get("phone"))
        result = await db.exec(query)
        existing = result.first()

        if not existing:
            logger.warning("Meter reader not found")
            return APIResponse.error(message="meter reader dont Exist", status_code=status.HTTP_404_NOT_FOUND)
        today = date.today().isoformat()
        blob_path = f"{meter_reader.get('phone')}/{phone}/{today}.png"
        file_content = await image.read()
        meter_url= await upload_blob(blob_path=blob_path, img_bytes=file_content)

        meter_reading = await meter_ocr(meter_url=meter_url)
        data = {
            "meter_reading": meter_reading,
            "blob_path": meter_url
        }
        return APIResponse.success(data=data, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Error in meter reading", exc_info=e)
        return APIResponse.error("Something went wrong with reading of meter reading")


@meter_reader_router.get("/calculate_bill", description="Calculate Bills")
async def calculate_bill(
        bill_data: CalculateBill,
        db: Session = Depends(get_session),
        meter_reader = Depends(get_token_data),
):
    query = select(Customers).where(Customers.phone == bill_data.phone)
    customer_result = await db.exec(query)
    customer = customer_result.first()
    if not customer:
        logger.warning("Customer not found")
        return APIResponse.error(message="Customer not found", status_code=404)

    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year

    # Check if a bill already exists for the current month
    last_bill_query = select(Bills).where(Bills.phone == bill_data.phone)
    last_bill = db.exec(last_bill_query).first()

    if last_bill:
        last_bill_date = datetime.strptime(last_bill.reading_date, "%Y-%m-%d").date()

        if last_bill_date.month == current_month and last_bill_date.year == current_year:
            return APIResponse.error(message="Bill for this month already exists", status_code=400)

        last_reading = last_bill.reading_value
    else:
        last_reading = 0.0

    # Calculate bill amount
    bill_amount = calculate_bill_amount(last_reading, bill_data.reading)

    # Set reading & due dates
    reading_date = current_date.strftime("%Y-%m-%d")  # Format 'YYYY-MM-DD'
    due_date = (current_date + timedelta(days=30)).strftime("%Y-%m-%d")  # Add 30 days

    # Create new bill entry
    new_bill = Bills(
        phone=bill_data.phone,
        reader_id=meter_reader.id,
        image_url=bill_data.image_url,
        reading_value=bill_data.reading,
        reading_date=reading_date,
        due_date=due_date,
        price=bill_amount,
        modified=bill_data.modified,
    )

    db.add(new_bill)
    await db.commit()
    await db.refresh(new_bill)

    return APIResponse.success(data=new_bill)




def calculate_bill_amount(old_reading,new_reading):
    reading_difference = new_reading - old_reading
    kiloliters = reading_difference/ 1000

    if reading_difference <= 5000:
        rate = 4
    elif 30000 <= reading_difference <= 40000:
        rate = 12
    else:
        rate = 8

    return int(kiloliters * rate)
