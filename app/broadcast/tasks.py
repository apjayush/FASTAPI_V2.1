from app.celery_app import celery_app
from app.broadcast.broadcast_payload_creator import build_payload, send_to_whatsapp
import asyncio
import os
from app.db import get_sync_connection

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
    user_id: int,            # <-- NEW
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

    try:
        # Celery is sync, so we must run async call manually
        response_json = asyncio.run(send_to_whatsapp(payload))
        status = "SUCCESS"
        error = None

    except Exception as e:
        status = "FAILED"
        error = str(e)

    conn = get_sync_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO message_logs 
            (user_id, phone_number, template_name, status, error_message)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_id,
                phone,
                template_name,
                status,
                error,
            ),
        )
        conn.commit()
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return {"status": status, "error": error, "response": response_json}



    