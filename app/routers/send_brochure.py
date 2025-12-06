from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

WHATSAPP_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


@router.post("/send-brochure")
async def send_brochure(payload: dict):

    print("send-brochure payload:", payload)  # for debugging

    to = payload.get("to")
    pdf_url = payload.get("pdf_url")
    filename = payload.get("filename", "brochure.pdf")
    caption = payload.get("caption", "")

    if not to or not pdf_url:
        raise HTTPException(status_code=400, detail="Missing 'to' or 'pdf_url'")

    # WhatsApp document message payload
    wa_payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "link": pdf_url,      # Public URL to PDF
            "caption": caption,
            "filename": filename
        }
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(WHATSAPP_URL, json=wa_payload, headers=headers)
            response.raise_for_status()

        return {"status": "success", "message": "Brochure sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
