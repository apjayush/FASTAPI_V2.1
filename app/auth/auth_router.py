import logging
from app.auth.jwt import get_current_user
from app.db import get_pool
from fastapi import APIRouter, Depends, HTTPException
from pwdlib import PasswordHash
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from pydantic import BaseModel
from fastapi import Response
import os
from dotenv import load_dotenv

load_dotenv()  # ✅ called ONCE

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


logger = logging.getLogger(__name__)

class LoginPayload(BaseModel):
    email: str
    password: str

password_hash = PasswordHash.recommended()

def create_access_token(data, expires_delta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    
@router.post("/login")
async def login_user(payload: LoginPayload, response: Response):
    pool = get_pool()
    if pool:
        async with pool.acquire() as conn:
            # Fetch user by email
            user = await conn.fetchrow('SELECT * FROM client_auth WHERE email = $1', payload.email)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
            
            # Verify password
            if not password_hash.verify(payload.password, user['password']):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
            
            # Create JWT token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user['email']}, expires_delta=access_token_expires
            )

            response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,          # 🔐 JS cannot read
            secure=False,            # ✅ HTTPS only (required in prod)
            samesite="Lax",         # ✅ prevents CSRF (change if cross-domain)
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

            logger.info(f"User {payload.email} logged in successfully ✅")

            return {"message": "Login successful"}
            
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database not available")
    

@router.get("/me")
def me(user: str = Depends(get_current_user)):
    """
    Frontend calls this to check if user is logged in.
    Returns 200 if valid cookie, 401 otherwise.
    """
    return {"email": user}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
