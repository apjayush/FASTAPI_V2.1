import httpx
import os
from dotenv import load_dotenv
load_dotenv()


WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"


def build_payload(to: str, template_name: str, language: str, params: list):
    return {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": p} for p in params
                    ],
                }
            ],
        },
    }


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
