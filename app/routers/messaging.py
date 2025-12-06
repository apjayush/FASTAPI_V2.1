from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.whatsapp_service import send_whatsapp_text
from app.utils.logger import log_message
from dotenv import load_dotenv
import os
import httpx
import asyncio

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

router = APIRouter()


class SendMessageRequest(BaseModel):
    to: str
    message: str


class NotifyAgentRequest(BaseModel):
    agent_phone: str  # Required - comes from Rasa action
    customer_name: str
    customer_phone: str


@router.post("/send-message")
async def send_message(payload: SendMessageRequest):
    """
    Send a plain text message to WhatsApp
    """
    print("=" * 60)
    print("📨 /send-message endpoint HIT")
    print(f"📞 To: {payload.to}")
    print("=" * 60)

    try:
        response = await send_whatsapp_text(
            to=payload.to,
            message=payload.message
        )
        
        log_message(f"✅ Message sent to {payload.to}")
        return {"status": "success", "response": response}
    
    except Exception as e:
        log_message(f"❌ Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify-agent")
async def notify_agent(payload: NotifyAgentRequest):
    """
    Notify agent about customer inquiry using custom template
    Template: new_enquiry_alert (works 24/7, no 24h window needed)
    """
    print("=" * 60)
    print("🔔 /notify-agent endpoint HIT")
    print(f"👤 Customer: {payload.customer_name} ({payload.customer_phone})")
    print(f"📞 Agent: {payload.agent_phone}")
    print("=" * 60)
    
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Send custom template with customer details
        whatsapp_link = f"https://wa.me/{payload.customer_phone}"
        
        template_payload = {
            "messaging_product": "whatsapp",
            "to": payload.agent_phone,
            "type": "template",
            "template": {
                "name": "new_customer_enquiry",
                "language": {
                    "code": "en"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": payload.customer_name  # {{1}} - Customer name (e.g., Ayush Aryan)
                            },
                            {
                                "type": "text",
                                "text": payload.customer_phone  # {{2}} - Customer phone (e.g., 918529750269)
                            },
                            {
                                "type": "text",
                                "text": whatsapp_link  # {{3}} - WhatsApp link (e.g., https://wa.me/918529750269)
                            }
                        ]
                    }
                ]
            }
        }
        
        print("📤 Sending custom template message to agent...")
        print(f"� Payload: {template_payload}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=template_payload, headers=headers)
            print(f"� Status: {response.status_code}")
            print(f"📊 Response: {response.text}")
            response.raise_for_status()
            result = response.json()
        
        print("✅ Template message sent to agent")
        
        log_message(f"✅ Agent {payload.agent_phone} notified about {payload.customer_name}")
        
        return {
            "status": "success",
            "message": "Agent notified successfully via custom template",
            "response": result
        }
    
    except httpx.HTTPStatusError as e:
        error_msg = f"WhatsApp API Error: {e.response.status_code} - {e.response.text}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
