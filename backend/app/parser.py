import os
import re
import pdfplumber
import docx2txt
import spacy
from typing import List, Dict, Optional

# Load NLP model (cache this in FastAPI app startup)
nlp = spacy.load("en_core_web_sm")

# --- Text Extraction ---
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF with proper page separation"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX while preserving structure"""
    return docx2txt.process(file_path)

def clean_text(text: str) -> str:
    """Normalize whitespace and clean artifacts"""
    text = re.sub(r'\n+', '\n', text)  # Collapse multiple newlines
    text = re.sub(r'[^\S\n]+', ' ', text)  # Collapse spaces (except newlines)
    return text.strip()

# --- Entity Extraction ---
def extract_entities(text: str) -> Dict[str, Optional[str]]:
    """
    Extract name (from first 2 lines), email, and phone.
    Returns: {'name': str, 'email': str, 'phone': str}
    """
    # Extract name from first 2 lines (where it usually appears)
    first_lines = '\n'.join(text.split('\n')[:2])
    doc = nlp(first_lines)
    name = ""
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.split('\n')[0].strip()  # Fix: Trim after newline
            break
    
    # Fallback: Use first line if no PERSON entity found
    if not name:
        name = text.split('\n')[0].strip().split('\t')[0].strip()
    
    # Extract email and phone (with validation)
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    phone_match = re.search(r'(\+?\d[\d\s\-()]{7,}\d)', text)
    
    return {
        "name": name if name else None,
        "email": email_match.group() if email_match else None,
        "phone": phone_match.group(1) if phone_match else None
    }

# --- Skills Extraction ---
def extract_skills(text: str, skill_list: List[str]) -> List[str]:
    """Find skills using case-insensitive whole-word matching"""
    found_skills = set()
    text_lower = text.lower()
    
    for skill in skill_list:
        # Match whole words only (avoid "Java" matching "JavaScript")
        if re.search(rf'\b{re.escape(skill.lower())}\b', text_lower):
            found_skills.add(skill)
    
    return sorted(found_skills)

# --- Education Extraction ---
def extract_education(text: str) -> List[str]:
    """Extract education degrees with flexible matching"""
    patterns = [
        r"(?:B\.?Tech|Bachelor[\s']*(?:of|in)?[\s']*Technology)\b.*?(?:Computer Science|Artificial Intelligence|IT|\bAI\b|\bCS\b)",
        r"(?:M\.?Tech|Master[\s']*(?:of|in)?[\s']*Technology)\b.*?(?:Data Science|Machine Learning)",
        r"B\.?[Ee]\.?\b.*?(?:Computer|Electrical)",
        r"B\.?[Ss]c\.?\b.*?(?:Computer|Physics|Mathematics)",
        r"\bPhD\b.*?(?:Computer Science|Engineering)"
    ]
    
    found = set()
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.update(m.strip() for m in matches)
    
    return sorted(found) if found else []

# --- Experience Extraction ---
def calculate_experience_years(experience_dates: List[str]) -> float:
    """Calculate total years of experience from date ranges"""
    total_years = 0.0
    
    for date_range in experience_dates:
        # Handle "YYYY-YYYY" format (e.g., 2020-2024)
        if re.match(r'\d{4}[\s\-–to]+\d{4}', date_range):
            start, end = map(int, re.findall(r'\d{4}', date_range))
            total_years += (end - start)
        
        # Handle "Month YYYY - Month YYYY" (e.g., "Jan 2020 - Dec 2023")
        elif re.match(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}', date_range):
            years = list(map(int, re.findall(r'\d{4}', date_range)))
            if len(years) == 2:
                total_years += (years[1] - years[0])
    
    return total_years

def extract_experience(text: str) -> List[str]:
    """Extract all experience date ranges"""
    patterns = [
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}[\s\-–to]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}',
        r'\d{4}[\s\-–to]+\d{4}'
    ]
    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text))
    return matches

# --- Main Parser ---
def parse_resume(file_path: str, company_requirements: Optional[Dict] = None) -> Dict:
    """Parse resume and return structured data"""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX files are supported")
    
    text = clean_text(text)
    
    # Define skills list (expand as needed)
    skills_list = [
        "Python", "Java", "SQL", "TensorFlow", "Keras", "Pandas", "Numpy",
        "Scikit-learn", "Power BI", "Excel", "Git", "Linux", "Tableau",
        "Deep Learning", "Machine Learning", "NLP", "Natural Language Processing",
        "Data Analysis", "Streamlit", "Matplotlib", "Seaborn", "Spark","Artificial Intelligence", "AI",
        "Computer Vision","Data Engineering", "Big Data"
    ]
    
    result = extract_entities(text)
    result["education"] = extract_education(text)
    result["experience"] = extract_experience(text)
    result["skills"] = extract_skills(text, skills_list)
    result["full_text"] = text  # Optional: useful for debugging
    if company_requirements:
        result["match_score"] = calculate_match_score(result, company_requirements)    
    return result

# --- Matching Algorithm ---
def calculate_match_score(
    candidate_data: Dict,
    company_requirements: Dict
) -> float:
    """Calculate match percentage (0-100) based on requirements"""
    score = 0.0
    total_weight = 0.0
    
    # Skills Matching (50% weight)
    candidate_skills = {s.lower() for s in candidate_data["skills"]}
    required_skills = {s.lower() for s in company_requirements.get("skills", [])}
    
    if required_skills:
        matched_skills = candidate_skills & required_skills
        skill_score = len(matched_skills) / len(required_skills) * 100
        score += skill_score * 0.5
        total_weight += 0.5
    
    # Education Matching (30% weight)
    candidate_edu = {e.lower() for e in candidate_data["education"]}
    required_edu = {e.lower() for e in company_requirements.get("education_keywords", [])}
    
    if required_edu:
        matched_edu = candidate_edu & required_edu
        edu_score = len(matched_edu) / len(required_edu) * 100
        score += edu_score * 0.3
        total_weight += 0.3
    
    # Experience Matching (20% weight)
    exp_years_required = company_requirements.get("experience_years_required", 0)
    if exp_years_required > 0:
        candidate_exp_years = calculate_experience_years(candidate_data["experience"])
        if candidate_exp_years >= exp_years_required:
            exp_score = 100  # Meets or exceeds requirement
        else:
            exp_score = (candidate_exp_years / exp_years_required) * 100  # Partial credit
        score += exp_score * 0.2
        total_weight += 0.2
    
    # Normalize score (in case some weights were 0)
    final_score = (score / total_weight) if total_weight > 0 else 0
    return round(final_score, 2)

# --- Example Usage ---
if __name__ == "__main__":
    # Example resume parsing
    resume_path = "C:/Users/pessh/Desktop/resume-parser-ai/backend/resume/resume.pdf"
    parsed_data = parse_resume("C:/Users/pessh/Desktop/resume-parser-ai/backend/resume/resume.pdf")
    
    # Example company requirements
    company_requirements = {
        "skills": ["Python", "SQL", "Machine Learning", "Pandas", "Deep Learning"],
        "education_keywords": ["B.Tech", "Bachelor of Technology", "Computer Science"],
        "experience_years_required": 1
    }
    
    # Calculate match score
    parsed_data["match_score"] = calculate_match_score(parsed_data, company_requirements)
    
    # Pretty print results
    from pprint import pprint
    pprint(parsed_data)
