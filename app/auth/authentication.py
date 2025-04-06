from datetime import timedelta, datetime
from typing import Optional

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import status, HTTPException, Depends

import jwt
from passlib.context import CryptContext

from utils.constant import SECRET_KEY, ALGORITHM
from utils.logger import logger
from utils.response import APIResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
        to_encode.update({"exp": expire})
    logger.debug("Created access token")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Expired token")
        return APIResponse.auth_required()
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return APIResponse.error("Token Provided Was Invalid",status_code=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.critical("Unknown Error while Decoding token", e)
        return APIResponse.error("Unknown Error",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_token_data(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"phone": payload.get("phone"),"email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        logger.error("Expired token")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")