from fastapi import APIRouter, Request
from app.db import create_pool
from app.repositories.customer_enquiry_repo import insert_customer_enquiry, update_customer_name
from app.utils.logger import log_message
from app.services.whatsapp_service import send_whatsapp_text
from app.services.rasa_service import send_to_rasa
from app.services.whatsapp_service import send_whatsapp_buttons
from app.services.user_message_validator import is_valid_message
import os

router = APIRouter()

# NEW: Global pool (initialize once)
pool = None

@router.on_event("startup")
async def startup_event():
    global pool
    pool = await create_pool()

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    # log_message(str(data))  # log full raw webhook content

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        # ---------------------------------------
        # IGNORE STATUS NOTIFICATIONS
        # (sent, delivered, read)
        # ---------------------------------------
        if "statuses" in value:
            return {"status": "ok"}

        # ---------------------------------------
        # GET USER MESSAGE
        # ---------------------------------------
        messages = value.get("messages", [])
        if not messages:
            return {"status": "no_messages"}

        msg = messages[0]
        user_phone = msg["from"]

        print(f"User Message: {msg}")  # for debugging
        print(f"User Phone: {user_phone}")

        # ---------------------------------------
        # CASE 1: USER SENT NORMAL TEXT
        # ---------------------------------------
        if msg["type"] == "text":
            user_msg = msg["text"]["body"]

            # NEW: If user says "Hi" or related, insert enquiry
        if user_msg.lower().strip() in ["hi", "hello", "hey"]:
            await insert_customer_enquiry(pool, user_phone, interested_in="general_inquiry")  # Customize interested_in

        # NEW: If user provides name (e.g., during booking flow), update name
        # Assuming Rasa or logic detects name input, e.g., if message looks like a name
        # elif is_name_input(user_msg):  # Helper to check if it's a name
        #     await update_customer_name(pool, user_phone, user_msg.strip())

            # filter poor message here
            if not is_valid_message(user_msg):
                await send_whatsapp_text(user_phone, "⚠️ Sorry, I didn't understand that. Could you please rephrase? For example, send 'Hi' and see about our services!")
                log_message(f"❌ Ignored poor message from {user_phone}: {user_msg}")
                return {"status": "ignored"}

        # ---------------------------------------
        # CASE 2: USER CLICKED A BUTTON
        # ---------------------------------------
        elif msg["type"] == "interactive":
            interactive = msg["interactive"]

            # Button reply
            if interactive["type"] == "button_reply":
                user_msg = interactive["button_reply"]["id"]

            # List reply (future)
            elif interactive["type"] == "list_reply":
                user_msg = interactive["list_reply"]["id"]

        else:
            user_msg = None

        # No valid message
        if not user_msg:
            return {"status": "ignored"}

        log_message(f"From: {user_phone} | Message: {user_msg}")

        # ---------------------------------------
        # SEND TO RASA
        # ---------------------------------------
        rasa_response = await send_to_rasa(user_phone, user_msg)
        log_message(f"Rasa replied: {rasa_response}")

        # ---------------------------------------
        # SEND RASA RESPONSES TO WHATSAPP
        # ---------------------------------------
        for r in rasa_response:

            # Buttons
            if r.get("buttons"):
                await send_whatsapp_buttons(
                    user_phone,
                    r.get("text", ""),
                    r["buttons"]
                )

            # Text only
            elif r.get("text"):
                await send_whatsapp_text(user_phone, r["text"])

        return {"status": "ok"}

    except Exception as e:
        log_message(f"Webhook Error: {e}")
        return {"status": "error"}
    


VERIFY_TOKEN= os.getenv("VERIFY_TOKEN") 
@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "Invalid verify token"}