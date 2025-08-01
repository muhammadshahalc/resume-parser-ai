import os
import asyncpg
import asyncio
import json
from fastapi import HTTPException
from dotenv import load_dotenv
from pathlib import Path

# Load the .env file from backend folder
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in the .env file!")
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

async def save_resume_result(data: dict):
    conn = None
    try:
        conn = await get_connection()
        await conn.execute('''
            INSERT INTO resume_results (
                name, email, phone, skills, 
                education, experience, match_score, raw_data
            ) VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6::jsonb, $7, $8::jsonb)
        ''',
        data.get('name'),
        data.get('email'),
        data.get('phone'),
        json.dumps(data.get('skills', [])),      # ✅ Convert list to JSON string
        json.dumps(data.get('education', [])),   # ✅ Convert list to JSON string
        json.dumps(data.get('experience', [])),  # ✅ Convert list to JSON string
        data.get('match_score', 0),
        json.dumps(data))                        # ✅ Convert full dict to JSON string
        await conn.close()
    except Exception as e:
        raise HTTPException(500, f"Database error: {str(e)}")
    finally:
        if conn:
            await close_connection(conn)




