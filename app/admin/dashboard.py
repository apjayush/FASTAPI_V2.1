# this end point will be used to show number of leads on the UI along with their name, number etc

from fastapi import APIRouter, HTTPException,status
from pydantic import BaseModel
from datetime import date
from fastapi import Depends
import json
from app.auth.jwt import get_current_user
from app.db import get_pool

router = APIRouter()

# class PayloadDetails(BaseModel):


@router.get("/dashboard")
async def send_enquiry_data(current_user = Depends(get_current_user)):
    # today_date = date.today()
    pool = get_pool()
    if pool:
        async with pool.acquire() as conn:
            # Fetch user by email
            lead_details = await conn.fetchrow("""
            select 
                count(id) as total,
                jsonb_agg(
                jsonb_build_object(
                'name', name,
                'number', phone,
                'enquiry_date', DATE(updated_at)
                )
                ) as details
                from customer_enquiry ce ;
            """)
            return {
                "total": lead_details["total"],
                "leads": json.loads(lead_details["details"])
            }
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database not available")