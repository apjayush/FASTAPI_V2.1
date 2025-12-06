import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "clinic")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_PORT = int(os.getenv("DB_PORT", 5432))


async def get_db_connection():
    """
    Returns a new database connection.
    Call this inside every FastAPI route where DB access is needed.
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=DB_PORT
    )
    return conn
