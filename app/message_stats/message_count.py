from fastapi import APIRouter, Depends, HTTPException, status
from app.db import get_pool
from app.auth.jwt import get_current_user
from datetime import date
from datetime import date


router = APIRouter(prefix="/messages", tags=["Message Stats"])

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_message_stats(
    current_user = Depends(get_current_user),
):
    pool = get_pool()
    if not pool:
        raise HTTPException(
            500, "Database connection pool not initialized"
        )

    user_id = int(current_user["user_id"])

    # get todays and date of this month
    current_date = date.today()
    first_day_of_month = current_date.replace(day=1)

    async with pool.acquire() as conn:
        total_messages_per_month = await conn.fetchval(
            """
            SELECT count(id) AS count_per_month
            FROM message_logs ml
            WHERE ml.status = 'SUCCESS'
            AND ml.sent_at between $1 and $2
            and ml.user_id = $3;
            """,
            first_day_of_month,
            current_date,
            user_id,
        )

        total_messages_today = await conn.fetchval(
            """
            SELECT count(id) AS count_per_day
            FROM message_logs ml
            WHERE ml.status = 'SUCCESS'
            AND ml.sent_at::date = $1
            and ml.user_id = $2;
            """,
            current_date,
            user_id,
        )

    return {
        "total_messages_per_month": total_messages_per_month,
        "total_messages_today": total_messages_today,
    }