from fastapi import APIRouter, HTTPException
from app.db import get_db_connection
from pydantic import BaseModel
from datetime import date
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()
DEFAULT_SLOTS = os.getenv("DEFAULT_SLOTS", "11AM,12PM,1PM").split(",")
MAX_CAPACITY = int(os.getenv("MAX_CAPACITY", 4))
DB_SCHEMA = os.getenv("DB_SCHEMA", "healthcare").strip()


@router.get("/available-slots")
async def available_slots():

    today = date.today()
    conn = await get_db_connection()

    # 1. Check if today's slots exist
    existing_rows = await conn.fetch(
        f"SELECT * FROM {DB_SCHEMA}.slots WHERE booking_date = $1",
        today
    )

    # 2. If no slots exist for today → create them
    if not existing_rows:
        for slot in DEFAULT_SLOTS:
            await conn.execute(
                f"""
                INSERT INTO {DB_SCHEMA}.slots (slot_time, booking_count, booking_date)
                VALUES ($1, 0, $2)
                """,
                slot,
                today
            )

        # Fetch again after insertion
        existing_rows = await conn.fetch(
            f"SELECT * FROM {DB_SCHEMA}.slots WHERE booking_date = $1",
            today
        )

    # 3. Get only available slots (booking_count < MAX_CAPACITY)
    available = [
        row["slot_time"]
        for row in existing_rows
        if row["booking_count"] < MAX_CAPACITY
    ]

    print("available slots:", available)  # for debugging

    return {"slots": available}


