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
    parameters: list,
    campaign_id: str,
):
    payload = build_payload(
        to=phone,
        template_name=template_name,
        language=language,
        params=parameters,
    )

    # Celery is sync → run async function properly
    asyncio.run(send_to_whatsapp(payload))
