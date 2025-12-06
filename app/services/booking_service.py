# Temporary in-memory storage for bookings
BOOKINGS_DB = {}

async def save_booking(name: str, slot: str, phone: str):
    # Create a simple appointment id
    appointment_id = len(BOOKINGS_DB) + 1

    # Insert into the dict
    BOOKINGS_DB[appointment_id] = {
        "id": appointment_id,
        "name": name,
        "slot": slot,
        "phone": phone,
    }

    print("✅ Booking saved with ID:", appointment_id)


    return appointment_id
