from fastapi import APIRouter, HTTPException
import os
import httpx

router = APIRouter()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")   # Your WhatsApp Business ID

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


@router.post("/send-list")
async def send_list(payload: dict):

    print("send-list payload:", payload)  # for debugging

    to = payload.get("to")
    header = payload.get("header", "")
    body = payload.get("body", "")
    button_text = payload.get("button_text", "View")
    sections = payload.get("sections", [])

    if not to or not sections:
        raise HTTPException(status_code=400, detail="Missing 'to' or 'sections' in request")

    # WhatsApp list message payload
    wa_payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": header
            },
            "body": {
                "text": body
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }

    print("wa_payload:", wa_payload)  # for debugging


    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            print("Sending request to WhatsApp API...")
            print("url is ", WHATSAPP_URL)
            response = await client.post(WHATSAPP_URL, json=wa_payload, headers=headers)
            print("response", response.text)
            response.raise_for_status()

        return {"status": "success", "detail": "List sent to WhatsApp"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
