import asyncpg
import logging
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

logger = logging.getLogger(__name__)

_pool = None  # Global pool variable

async def create_pool():
    global _pool
    if _pool:
        return _pool
    _pool = await asyncpg.create_pool(
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '123'),
        database=os.getenv('DB_NAME', 'automobiles'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        min_size=5,
        max_size=10
    )
    if _pool:
        logger.info("Database connection pool created successfully ✅")
        return _pool
    else:
        logger.error("Failed to create database connection pool ❌")
        return None

def get_pool():
    """Return the global connection pool."""
    return _pool

async def close_pool(pool=None):
    global _pool
    if pool is None:
        pool = _pool
    if pool:
        await pool.close()
        _pool = None


def get_sync_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

if __name__ == '__main__':
    async def main():
        pool = await create_pool()
        async with pool.acquire() as connection:
            result = await connection.fetchval('SELECT 1 + 1')
            print(f"Result of 1 + 1: {result}")