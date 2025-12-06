from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import get_db_connection
# from app.services.booking_service import save_booking
from datetime import date
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()
DB_SCHEMA = os.getenv("DB_SCHEMA", "healthcare").strip()
MAX_CAPACITY = int(os.getenv("MAX_CAPACITY", 4))
DEFAULT_SLOTS = os.getenv("DEFAULT_SLOTS", "11AM,12PM,1PM").split(",")

# --------- REQUEST BODY MODEL ----------
class BookingRequest(BaseModel):
    name: str
    slot: str       # example: "11AM"
    phone: str


@router.post("/book-slot")
async def book_slot(payload: BookingRequest):

    name = payload.name
    slot_time = payload.slot.strip()
    phone = payload.phone.strip()
    today = date.today()

    print("Today:", today)  # for debugging
    phone = "8529750268"

    # slot_time is coming like 11 AM
    slot_time = slot_time.replace(" ", "").upper()

    conn = await get_db_connection()

    print(slot_time,today)

    # 1️⃣ FIND THE SLOT ROW FOR TODAY
    slot_row = await conn.fetchrow(
        f"""
        SELECT * FROM {DB_SCHEMA}.slots
        WHERE slot_time = $1
        AND booking_date = $2
        """,
        slot_time,
        today
    )

    print("slot_row:", slot_row)  # for debugging

    if not slot_row:
        raise HTTPException(
            status_code=400,
            detail=f"Slot '{slot_time}' not found for today"
        )

    # If slot is already full
    if slot_row["booking_count"] >= MAX_CAPACITY:
        raise HTTPException(
            status_code=400,
            detail=f"Slot {slot_time} is fully booked"
        )

    slot_id = slot_row["id"]

    # 2️⃣ CHECK IF USER IS ALREADY BOOKED FOR THIS SLOT
    existing_booking = await conn.fetchrow(
        f"""
        SELECT * FROM {DB_SCHEMA}.appointments
        WHERE slot_id = $1 AND phone = $2
        """,
        slot_id,
        phone
    )

    if existing_booking:
        raise HTTPException(
            status_code=400,
            detail=f"User already booked this slot"
        )

    # 3️⃣ INSERT INTO APPOINTMENTS
    await conn.execute(
        f"""
        INSERT INTO {DB_SCHEMA}.appointments (slot_id, name, phone)
        VALUES ($1, $2, $3)
        """,
        slot_id,
        name,
        phone
    )

    # 4️⃣ INCREMENT booking_count
    await conn.execute(
        f"""
        UPDATE {DB_SCHEMA}.slots
        SET booking_count = booking_count + 1
        WHERE id = $1
        """,
        slot_id
    )

    return {
        "status": "success",
        "message": "Appointment booked successfully",
        "slot": slot_time,
        "name": name,
        "phone": phone
    }
