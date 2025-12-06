import httpx
from app.config import WHATSAPP_TOKEN, PHONE_NUMBER_ID


async def send_whatsapp_text(to: str, message: str):
    """
    Send a plain text message to a WhatsApp user.
    """

    print("Reaching WhatsApp API to send message")

    print(message)
    
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    print("WhatsApp URL:", url)

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        print("WhatsApp response status:", response.status_code)
        return response.json()


async def send_whatsapp_buttons(to: str, text: str, buttons: list):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    print("Reacheding WhatsApp API to send buttons")

    # Convert Rasa buttons → WhatsApp buttons
    wa_buttons = []
    for b in buttons:
        wa_buttons.append({
            "type": "reply",
            "reply": {
                "id": b["payload"],   # WhatsApp returns this when user clicks
                "title": b["title"]   # Button text (max 20 chars)
            }
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": text.strip()
            },
            "action": {
                "buttons": wa_buttons
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    print("payload", payload)
    print("headers", headers)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
    


async def send_whatsapp_list(to: str, header: str, body: str, button_text: str, sections: list):
    """
    Send a WhatsApp list message (for more than 3 options)
    
    Args:
        to: WhatsApp phone number
        header: List header text
        body: Main message text
        button_text: Text on the button that opens the list (e.g., "View Vehicles")
        sections: List of sections, each containing rows
        
    Example sections:
    [
        {
            "title": "Available Bikes",
            "rows": [
                {"id": "apache_rtr_160", "title": "Apache RTR 160", "description": "Sports bike"},
                {"id": "2004v", "title": "TVS Apache 200 4V", "description": "Premium sports"},
                {"id": "tvs_jupiter", "title": "TVS Jupiter", "description": "Scooter"},
                {"id": "tvs_ronin", "title": "TVS Ronin", "description": "Cruiser bike"}
            ]
        }
    ]
    """
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    print("Reaching WhatsApp API to send list")

    payload = {
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

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    print("List payload:", payload)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()


