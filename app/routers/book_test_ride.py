from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import get_db_connection
from app.services.whatsapp_service import send_whatsapp_text
from datetime import date
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()
DB_SCHEMA = os.getenv("DB_SCHEMA", "healthcare").strip()
# MAX_CAPACITY = int(os.getenv("MAX_CAPACITY", 4))
# DEFAULT_SLOTS = os.getenv("DEFAULT_SLOTS", "11AM,12PM,1PM").split(",")

# ...existing code...

# --------- TEST RIDE REQUEST MODEL ----------
class TestRideRequest(BaseModel):
    name: str
    phone: str
    vehicle: str = None  # Optional: if user selected a vehicle

@router.post("/book-test-ride")
async def book_test_ride(payload: TestRideRequest):
    """
    Book a test ride and send confirmation via WhatsApp
    """
    name = payload.name.strip()
    phone = payload.phone.strip()
    vehicle = payload.vehicle or "Not specified"
    today = date.today()

    print(f"📝 Booking test ride for {name} ({phone}) - Vehicle: {vehicle}")

    try:
        # Create confirmation message
        confirmation_message = f"""✅ *Test Ride Booked Successfully!*

👤 Name: {name}
🏍️ Vehicle: {vehicle}
📞 Phone: {phone}

📍 Location: BLR TVS MOTORS
⏰ Our team will contact you shortly to confirm the date and time.

Thank you for choosing TVS Motors! 🚀"""

        # Send confirmation message directly via WhatsApp
        print(f"📤 Sending confirmation message to {phone}...")
        await send_whatsapp_text(
            to=phone,
            message=confirmation_message
        )


    except Exception as e:
        print(f"❌ Error booking test ride: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")