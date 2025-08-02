from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_resume
from database import save_resume_result
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


COMPANY_REQUIREMENTS = {
    "skills": ["Python", "SQL", "Machine Learning", "Pandas", "Deep Learning"],
    "education_keywords": ["B.Tech", "Bachelor of Technology", "Computer Science"],
    "experience_years_required": 1
}


@app.post("/api/parse")
async def parse_resume_route(file: UploadFile):
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(400, "Only PDF and DOCX files are supported")
    
    temp_path = None
    try:
        
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())
        
        
        result = parse_resume(temp_path, COMPANY_REQUIREMENTS)
        
        
        await save_resume_result(result)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
