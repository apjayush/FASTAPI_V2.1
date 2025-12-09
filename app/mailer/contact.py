from fastapi import APIRouter, HTTPException, Request
from typing_extensions import Annotated
from pydantic import BaseModel, EmailStr, Field
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import phonenumbers
from email.message import EmailMessage
import aiosmtplib
import logging

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("contact-api")


class ContactIn(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    email: EmailStr
    phone: Annotated[str, Field(min_length=6)]
    message: Annotated[str, Field(min_length=1)]


def validate_phone(value: str) -> str:
    try:
        parsed = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")
    except Exception:
        raise ValueError("Invalid phone number")
    return value


async def send_email(contact: ContactIn) -> None:
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("SMTP credentials not configured. Set SMTP_USER and SMTP_PASS in environment.")

    msg = EmailMessage()
    msg["From"] = contact.email
    msg["To"] = SMTP_USER
    msg["Subject"] = f"Contact form: {contact.name}"

    body = f"""
New contact form submission

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone}

Message:
{contact.message}
"""
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASS,
    )


@router.post("/contact")
async def contact_endpoint(contact: ContactIn, request: Request):
    try:
        validate_phone(contact.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        await send_email(contact)
    except RuntimeError as e:
        logger.exception("SMTP not configured")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception("Failed to send email")
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"ok": True, "message": "Email sent"}
