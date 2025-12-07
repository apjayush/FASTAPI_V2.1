# app/core/security.py

import jwt
from fastapi import Request, HTTPException, status
from datetime import timezone
import os
from dotenv import load_dotenv

load_dotenv()  # ✅ called ONCE

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def get_current_user(request: Request) -> str:
    """
    Validates JWT from HttpOnly cookie and returns user identity.
    Runs BEFORE protected routes.
    """

    # ✅ Extract token from cookie
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        # ✅ Decode & validate JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        print(payload)

        user_identity = payload.get("sub")
        if not user_identity:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return user_identity

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
