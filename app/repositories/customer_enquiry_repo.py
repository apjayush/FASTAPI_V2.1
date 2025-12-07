# NEW: Insert a new customer enquiry
import logging

logger = logging.getLogger(__name__)


async def insert_customer_enquiry(pool, phone: str, interested_in: str = None):
    """Insert a new customer enquiry."""
    async with pool.acquire() as connection:
        try:
            await connection.execute(
                "INSERT INTO customer_enquiry (phone, interested_in) VALUES ($1, $2) ON CONFLICT (phone) DO NOTHING",
                phone, interested_in
            )
            logger.info(f"✅ Inserted enquiry for {phone}")
        except Exception as e:
            logger.error(f"❌ Error inserting enquiry: {e}")

# NEW: Update customer name in enquiry
async def update_customer_name(pool, phone: str, name: str):
    """Update the customer's name."""
    async with pool.acquire() as connection:
        try:
            await connection.execute(
                "UPDATE customer_enquiry SET name = $1, updated_at = CURRENT_TIMESTAMP WHERE phone = $2",
                name, phone
            )
            logger.info(f"✅ Updated name for {phone}: {name}")
        except Exception as e:
            logger.error(f"❌ Error updating name: {e}")
