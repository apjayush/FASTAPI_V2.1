from fastapi import APIRouter, Depends, HTTPException, status
from uuid import uuid4
from pydantic import BaseModel
from typing import List
from app.auth.jwt import get_current_user
from app.broadcast.tasks import send_whatsapp_task


class BroadcastRequest(BaseModel):
    template_id: str
    template_name: str
    language: str
    recipients: List[str]
    parameters: List[str] = []


router = APIRouter(prefix="/broadcast", tags=["Broadcast"])


@router.post("/send", status_code=status.HTTP_202_ACCEPTED)
async def send_broadcast(
    payload: BroadcastRequest,
    user_email: str = Depends(get_current_user),
):
    if not payload.recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No recipients provided",
        )

    campaign_id = str(uuid4())

    for number in payload.recipients:
        send_whatsapp_task.delay(
            phone=number,
            template_name=payload.template_name,
            language=payload.language,
            parameters=payload.parameters,
            campaign_id=campaign_id,
        )

    return {
        "status": "queued",
        "campaign_id": campaign_id,
        "total_recipients": len(payload.recipients),
    }
