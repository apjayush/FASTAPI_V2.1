from fastapi import APIRouter, HTTPException, status, Depends
import httpx
import os
from app.auth.jwt import get_current_user

router = APIRouter()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
BUSINESS_ID = os.getenv("WHATSAPP_BUISNESS_ID")


@router.get("/message-templates")
async def get_message_templates(user_email: str = Depends(get_current_user)):
    url = f"https://graph.facebook.com/v23.0/{BUSINESS_ID}/message_templates"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch WhatsApp templates",
        )

    data = response.json().get("data", [])

    templates = []
    for t in data:
        body = ""
        params = 0

        has_header = False
        header_format = None           # e.g. "IMAGE", "TEXT", "VIDEO"
        header_example_url = None      # first example header_handle URL

        has_footer = False
        footer_text = None

        has_buttons = False
        buttons = []                   # optional: to show quick replies/CTAs in UI

        for comp in t.get("components", []):
            ctype = comp.get("type")

            # BODY
            if ctype == "BODY":
                body = comp.get("text", "") or ""
                params = body.count("{{")

            # HEADER
            if ctype == "HEADER":
                has_header = True
                header_format = comp.get("format")  # "IMAGE", "TEXT", "VIDEO", etc.
                # For media headers, Meta returns example.header_handle
                example = comp.get("example") or {}
                header_handles = example.get("header_handle") or []
                if header_handles:
                    header_example_url = header_handles[0]

            # FOOTER
            if ctype == "FOOTER":
                has_footer = True
                footer_text = comp.get("text")

            # BUTTONS
            if ctype == "BUTTONS":
                has_buttons = True
                buttons = comp.get("buttons", [])

        templates.append(
            {
                "id": t["id"],
                "name": t["name"],
                "category": t.get("category"),
                "language": t.get("language"),
                "status": t.get("status"),
                "body": body,
                "param_count": params,
                "has_header": has_header,
                "header_format": header_format,
                "header_example_url": header_example_url,
                "has_footer": has_footer,
                "footer_text": footer_text,
                "has_buttons": has_buttons,
                "buttons": buttons,
            }
        )

    return templates
