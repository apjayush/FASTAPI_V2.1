from app.celery_app import celery_app
from app.broadcast.broadcast_payload_creator import build_payload, send_to_whatsapp
import asyncio


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def send_whatsapp_task(
    self,
    phone: str,
    template_name: str,
    language: str,
    header_image_url: str,   # <-- NEW
):
    """
    Celery worker task to send WhatsApp messages.
    """
    
    # Build WhatsApp payload (no body params now)
    payload = build_payload(
        to=phone,
        template_name=template_name,
        language=language,
        header_image_url=header_image_url,  # <-- NEW
        body_params=None,                   # <-- No body params anymore
    )

    # Celery is sync, so we must run async call manually
    asyncio.run(send_to_whatsapp(payload))
