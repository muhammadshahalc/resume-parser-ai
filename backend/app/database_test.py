import asyncpg
import os
import asyncio
import json
from fastapi import HTTPException
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the same directory as this script
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL missing in .env!")

pool = None

async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

async def get_connection():
    if pool is None:
        await create_pool()
    return await pool.acquire()

async def close_connection(conn):
    await pool.release(conn)

async def test_connection():
    try:
        conn = await get_connection()
        print("✅ Successfully connected to PostgreSQL!")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        if conn:
            await close_connection(conn)

# Run the test
if __name__ == "__main__":
    asyncio.run(test_connection())