from fastapi import APIRouter, HTTPException,status
import httpx
import os
from fastapi import Depends
from app.auth.jwt import get_current_user

router = APIRouter()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
BUSINESS_ID = os.getenv("WHATSAPP_BUISNESS_ID")   # Your WhatsApp Business ID

@router.get("/message-templates")
async def get_message_templates(user_email: str = Depends(get_current_user)):
    url = f"https://graph.facebook.com/v23.0/{BUSINESS_ID}/message_templates"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch WhatsApp templates"
        )

    data = response.json().get("data", [])

    templates = []
    for t in data:
        if t.get("status") != "APPROVED":
            continue

        body = ""
        params = 0

        for comp in t.get("components", []):
            if comp["type"] == "BODY":
                body = comp.get("text", "")
                params = body.count("{{")

        templates.append({
            "id": t["id"],
            "name": t["name"],
            "category": t.get("category"),
            "language": t.get("language"),
            "body": body,
            "param_count": params
        })

    return templates
