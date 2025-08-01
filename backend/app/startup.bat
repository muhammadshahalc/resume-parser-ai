@echo off

REM Activate the virtual environment
call ..\..\venv\Scripts\activate.bat

REM Initialize the database connection pool
python -c "import asyncio; from database import create_pool; asyncio.get_event_loop().run_until_complete(create_pool())"

REM Start the FastAPI server using python -m uvicorn
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000


