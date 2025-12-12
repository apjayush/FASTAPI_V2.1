import httpx
import os
from dotenv import load_dotenv
from typing import Optional, List

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"


def build_payload(
    *,
    to: str,
    template_name: str,
    language: str = "en",
    header_image_url: Optional[str] = None,
    body_params: Optional[List[str]] = None,
):
    components = []

    # ✅ Header IMAGE (only if required)
    if header_image_url:
        components.append({
            "type": "header",
            "parameters": [
                {
                    "type": "image",
                    "image": {
                        "link": header_image_url
                    }
                }
            ],
        })

    # ✅ Body parameters
    if body_params:
        components.append({
            "type": "body",
            "parameters": [
                {"type": "text", "text": str(p)}
                for p in body_params
            ],
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }

    if components:
        payload["template"]["components"] = components

    return payload


async def send_to_whatsapp(payload: dict):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            WHATSAPP_URL, json=payload, headers=headers
        )

    if response.status_code not in (200, 201):
        raise Exception(response.text)
    
    return response.json()
