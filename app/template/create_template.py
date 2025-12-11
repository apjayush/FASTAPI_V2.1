# FastAPI has a strict rule:
# If even ONE parameter is a file (UploadFile or bytes), the entire request must be multipart/form-data.
# You CANNOT combine JSON body (Pydantic model) with File in the same request.

from fastapi import APIRouter, HTTPException, File, Form, UploadFile, status, Depends
from typing import Optional
from app.db import get_pool
from app.auth.jwt import get_current_user
from dotenv import load_dotenv
import os
import httpx
import uuid
from pathlib import Path

load_dotenv()


router = APIRouter(prefix="/templates", tags=["Create Template"]) 

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
BUSINESS_ID = os.getenv("WHATSAPP_BUISNESS_ID")


async def upload_image_bytes_to_meta(image_bytes: bytes, filename: str) -> str:

    url = "https://graph.facebook.com/v21.0/app/uploads"

    params = {
        "file_length": len(image_bytes),
        "file_type": "image/jpeg"
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/octet-stream",  # raw binary upload
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        session_resp = await client.post(
            url,
            params=params,
            headers=headers,
            content=image_bytes  # RAW BYTES, like '@file.png'
        )

        if session_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to create upload session: {session_resp.text}",
            )
        upload_id = session_resp.json()["id"]


        # 2. Upload bytes
        upload_resp = await client.post(
            f"https://graph.facebook.com/v21.0/{upload_id}",
            headers={
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "file_offset": "0"
            },
            content=image_bytes
        )
        if upload_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to upload image: {upload_resp.text}",
            )

        # 3. Return handle
        return upload_resp.json()["h"]




@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_template(
    user_email: str = Depends(get_current_user),
    media: Optional[UploadFile] = File(None),
    name: str = Form(...),
    category: str = Form(...),
    language: str = Form(...),
    body: str = Form(...),
    footer: Optional[str] = Form(None)
):

    filtered_name = name.strip().lower().replace(" ", "_")

    if not filtered_name or not body.strip():
        raise HTTPException(status_code=400, detail="Name and body required")
    
    components = [
        {
            "type": "BODY",
            "text": body
        }
    ]


    # ************////Important//////************
    # body was required anyhow so we have kept the body inside components
    # now we will check for footer, buttons header we will not check because that will be
    # handled in another else condtion since it requires 3 curls

    if media is None:

        if footer:
            components.append({
                "type": "FOOTER",
                "text": footer
            })


        payload_for_meta = {
            "name": filtered_name,
            "language": language,
            "category": category,
            "components": components
        }

        url = f"https://graph.facebook.com/v21.0/{BUSINESS_ID}/message_templates"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload_for_meta)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to create template: {response.text}",
            )

        return {"message": "Template created successfully", "response": response.json()}

    else:

        # 1) Read image bytes from UploadFile
        image_bytes = await media.read()

        ext = os.path.splitext(media.filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"

        BASE_DIR = Path(__file__).resolve().parent
        MEDIA_ROOT = (BASE_DIR / ".." / ".." / "media").resolve()
        TEMPLATE_MEDIA_DIR = MEDIA_ROOT / "templates"
        TEMPLATE_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

        # local_path_of_media
        local_path = os.path.join(TEMPLATE_MEDIA_DIR, unique_name)

        with open(local_path, "wb") as f:
            f.write(image_bytes)

        relative_path = f"media/templates/{unique_name}"

        # 4) Upload to Meta and get handle
        handle = await upload_image_bytes_to_meta(image_bytes, media.filename)

                # 5) Add HEADER component before BODY
        header_component = {
            "type": "HEADER",
            "format": "IMAGE",
            "example": {
                "header_handle": handle
            }
        }
        components.insert(0, header_component)  # HEADER at index 0

        # 6) Optional FOOTER if provided
        if footer and footer.strip():
            components.append({
                "type": "FOOTER",
                "text": footer.strip()
            })

        # 7) Build final payload for Meta
        payload_for_meta = {
            "name": filtered_name,
            "language": language,
            "category": category,
            "components": components
        }

        # 8) Call Meta template API
        url = f"https://graph.facebook.com/v21.0/{BUSINESS_ID}/message_templates"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload_for_meta)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to create template with image: {response.text}",
            )

        data = response.json()
        template_id = data.get("id")

        # 9) (Optional) store mapping template_id ↔ local_path in DB here

        pool = get_pool()
        if pool:
            async with pool.acquire() as conn:
                try:
                    await conn.execute(
                        "INSERT INTO templates (template_id, template_img_path) VALUES ($1, $2)",
                        template_id, relative_path
                    )
                except Exception as e:
                    print(f"❌ Error saving template media info: {e}")
                    return{
                        "message": "Error inserting media in database"
                    }

                
        return {
            "message": "Template with image created successfully",
            "template_id": template_id,
            "local_path": local_path,
            "meta_response": data
        }


        
        



    