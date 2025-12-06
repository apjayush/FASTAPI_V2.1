from fastapi import APIRouter, Request
from app.utils.logger import log_message
from app.services.whatsapp_service import send_whatsapp_text
from app.services.rasa_service import send_to_rasa
from app.services.whatsapp_service import send_whatsapp_buttons

router = APIRouter()

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
    


VERIFY_TOKEN = "mytoken"   
@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "Invalid verify token"}