from dotenv import load_dotenv
import os

load_dotenv()
POSTGRES_USERNAME = "postgres"
POSTGRES_PASSWORD= "postgres"
POSTGRES_HOST= "localhost:5432"
POSTGRES_DBNAME= "WaterBilling"
DB_URL= f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DBNAME}"

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


API_KEY = os.getenv('API_KEY_OCR')
END_POINT = os.getenv('END_POINT_OCR')
SAS_URL = os.getenv('SAS_URL')
CONTAINER_NAME = "bill-img"
