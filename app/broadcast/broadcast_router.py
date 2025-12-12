from tempfile import template
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import uuid4
from pydantic import BaseModel
from typing import List
from app.auth.jwt import get_current_user
from app.broadcast.tasks import send_whatsapp_task
from app.db import get_pool


class BroadcastRequest(BaseModel):
    template_id: str
    recipients: List[str]
    has_header: bool = False
    template_name: str
    template_language: str
    header_format: str = "IMAGE"  # Currently only IMAGE supported


router = APIRouter(prefix="/broadcast", tags=["Broadcast"])


@router.post("/send", status_code=status.HTTP_202_ACCEPTED)
async def send_broadcast(
    payload: BroadcastRequest,
    user_email: str = Depends(get_current_user),
):
    if not payload.recipients:
        raise HTTPException(
            status_code=400, detail="No recipients provided"
        )

    pool = get_pool()
    if not pool:
        raise HTTPException(
            500, "Database connection pool not initialized"
        )

    # ------------------------------------------
    # 1️⃣ Fetch template details from DB if has_header is true
    # ------------------------------------------
    header_image_url = None

    if payload.header_format == "IMAGE":
        async with pool.acquire() as conn:
            template = await conn.fetchrow(
                """
            SELECT template_img_path
            FROM templates
            WHERE template_id = $1
            """,
            payload.template_id,
        )


        img_path = template["template_img_path"]

        # ------------------------------------------
        # 2️⃣ If template needs HEADER IMAGE → fetch media URL
        # ------------------------------------------
        
        header_image_url = f"https://1eb33ea5a027.ngrok-free.app/{img_path}"

        print("Header image URL:", header_image_url)  # --- IGNORE ---

        
    # ------------------------------------------
    # 3️⃣ Send to Celery for each recipient
    # ------------------------------------------
    campaign_id = str(uuid4())

    for number in payload.recipients:
        send_whatsapp_task.delay(
            phone=number,
            template_name=payload.template_name,
            language=payload.template_language,
            header_image_url=header_image_url,
        )

    return {
        "status": "queued",
        "campaign_id": campaign_id,
        "total_recipients": len(payload.recipients),
    }
